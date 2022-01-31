#!/usr/bin/env python3
# File: actor_critic_1ed.py

import random
import numpy as np

import copy
from collections import deque # OrderedDict

from .strategy import Strategy


class Actor_critic_1ed(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)
        
        # state_length limits string length to memory_depth if memory is maintained deeper than memory_depth
        #   was added before memory_depth was enforced over the size of the deque, so not sure it is still necessary 
        #   however it does not affect anything else (05032021)
        self.state_length = 2 * self.options["memory_depth"]
        '''
        RL method
        actor-critic, Sutton&Barto 1st edition
        
        '''
        
        self.memory = deque(maxlen=int(self.options["memory_depth"]))
        self.state = ""
        self.prev_state = ""
        
        # initialise p_a, V

        
        self.smv = {"": [0.5,0.5]}
        self.p_a = {"": [0,0]}
        self.V = {"": 0}


    def action(self, agent, previous_step) -> int:
        '''     
            
            
            t       : timestep
            r       : reward at t
            smv     : softmax_values (action probabilities)
            p_a     : actor preferences
            V       : critic values
            alpha:  : critic learning rate
            beta    : actor learning rate
            gamma   : td_error discount factor
            # temperature : boltzmann temperature
            
            
            softmax on numerical preference of action (S&B, 2ed, p37)
            
        '''
        super().action(agent, previous_step)
        
        # TODO - draw from a_p ?
        ''' first move, act according to distribution supplied by option '''
        if len(agent.action_history) == 0:
            rnd = random.random()
            if rnd > (1 - self.options["initial_action"]):
                action = 1
            else:
                action = 0
        
        else:
            prev_action = previous_step[agent.agent_id]

            '''
                obtain reward from last action
                    type(r) == int
                r is stored in agent object as matrix payoff from last action
                if no previous reward (i.e. this is the first round, then previous_reward == 0
            '''
            # 3a)
            r = agent.previous_reward


            # 3b) record state
            ''' 
            append previous_step actions to agent memory
            previous_step is a tuple (n, n); n = (0|1)
                where 
                    position indicates agent (0 or 1)
                    value indicates action (0, or 1)
            '''
            self.memory.append(previous_step)
            
            '''
                translate n most recent paired actions to str
                    where 
                        n = self.memory_depth
                    gives 
                        len(self.state) == 2 * self.memory_depth
            '''
            self.state = self.memory_to_state_key()

            '''
                if state key not in V, p_a, smv tables, add key with default values
                    where 
                        values are list of two floats
                        position indicates action (e.g. 0 = UP, or C; 1 = DOWN, or D)
            '''
            if self.state not in self.V:
                self.V[self.state] = 0
                
            if self.state not in self.p_a:
                self.p_a[self.state] = [0, 0]
                
            if self.state not in self.smv:
                self.smv[self.state] = [0.5, 0.5]
            
            
            # 4 calc TD error
            '''
                td_error = r + (gamma * V[state]) - V[prev_state]
            ''' 

            td_error = r + (self.options["gamma"] * self.V[self.state]) - self.V[self.prev_state]

            # update critic
            self.V[self.prev_state] = self.V[self.prev_state] + (self.options["alpha"] * td_error)

            # update actor - update preferences for actions
            self.p_a[self.prev_state][prev_action] = self.p_a[self.prev_state][prev_action] + (self.options["beta"] * td_error)
            

            
            '''
                softmax
                self.options["temperature"] -- no temperature used in this algorithm (see S&B 1ed, p42)
                
                BUT, seee Crites & Barto 1995
                    refactor to use numpy with p=dist: np.random.choice([q_t_0, q_t_1], p=[q_t_0, q_t_1]) [TODO?]
                    - np.exp 'removes' overflows ... 
                
                To avoid overflows, is now rewritten to make use of the shift-invariant property of softargmax, i.e. exp-normalization.
                    code is broken down to constituent parts, rather than use numpy for now
                    
            '''          
            
            max_element = max(self.p_a[self.prev_state])

            numerator_0 = np.exp(self.p_a[self.prev_state][0] - max_element)
            numerator_1 = np.exp(self.p_a[self.prev_state][1] - max_element)
                

            # check for np.isinf() over numerators
            # if this occurs, just carry on, using old values .. but print to stdout so can _do something_ 
            # try catch [TODO]
            
            if np.isinf([numerator_0, numerator_1]).any():
                print(f"out of range in np.exp at {len(agent.action_history)}: {numerator_0}, {numerator_1}")
            else:
                denominator = numerator_0 + numerator_1
                
                self.smv[self.prev_state][0] = numerator_0 / denominator
                self.smv[self.prev_state][1] = numerator_1 / denominator
                
            # note (020921) was previous state not current state.
            #   previous code: if rnd < self.smv[self.prev_state][0]:
            #   so, code was drawing off smv at t. should/appears to be t.
            #   so, code calculates smv at t+1 (self.state not self.prev_state) and _then_ draws action from the smv. i.e., after it has processed incoming reward. 
            #
            #   added for release 2 of equivalence-study on 01/02/2022 
            rnd = random.random()
            if rnd < self.smv[self.state][0]:
                action = 0
            else:
                action = 1
                

        
        
        # 7. state -> previous_state
        '''
            push current state into the past
        '''
        self.prev_state = self.state
        
        return action
    

  

    def get_strategy_internal_state(self):
        return { "current_state" : self.state, "smv" : copy.deepcopy(self.smv), "p_a" : copy.deepcopy(self.p_a), "V" : copy.deepcopy(self.V) }

       
if __name__ == '__main__':
    print(self.options["name"])