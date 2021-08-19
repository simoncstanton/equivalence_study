#!/usr/bin/env python3
# File: actor_critic_1ed_eligibility_traces.py

import random
import numpy as np

import copy
from collections import deque # OrderedDict,

from .strategy import Strategy


class Actor_critic_1ed_eligibility_traces(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        self.state_length = 2 * self.options["memory_depth"]
        '''
        RL method
        actor-critic, Sutton&Barto 1st edition
        with eligibility traces
        1 trace for state (critic)
        trace for state-action (actor)
        
            [ initial values for V, actor trace?][TODO]
        '''
        
        self.memory = deque(maxlen=int(self.options["memory_depth"]))
        self.state = ""
        self.prev_state = ""
        
        
        self.smv = {"": [0.5,0.5]}
        self.p_a = {"": [0,0]}
        self.V = {"": 0}
        
        self.actor_trace = {"": [0, 0]}
        self.critic_trace = {"": 0}
        

    def action(self, agent, previous_step) -> int:
        '''     
            
            
            t       : timestep
            r       : reward at t
            smv     : action probabilities 
            p_a     : preference for actions, given state
            V       : state value 
            beta    : positive step-size parameter
            alpha   : step-size parameter
            gamma   : discount factor
            lambda  : positive step-size parameter
            temperature : boltzmann temperature
                (S&B have no temperature for this algorithm)
            
            softmax on numerical preference of action (S&B, 2ed, p37)
            
            - ? initial values for actor trace?
            
        '''
        super().action(agent, previous_step)
        
        # 2 TODO - draw from smv ?
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


            # 3b) note state
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
                if state key not in Q table, add key with default values
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
            
            if self.state not in self.critic_trace:
                self.critic_trace[self.state] = 0
            
            if self.state not in self.actor_trace:
                self.actor_trace[self.state] = [0, 0]
            
            
            
            td_error = r + (self.options["gamma"] * self.V[self.state]) - self.V[self.prev_state]
            
            
            ''' 
                Critic with trace 
                    as for TD_lambda
            
                1. calc td_error
                2. increment critic trace
                3. update critic trace with td_error * trace
                4. update critic 
            '''
                        
            self.critic_trace[self.prev_state] += 1
          
            for i, s in enumerate(self.V):
                self.V[s] = self.V[s] + self.options["alpha"] * td_error * self.critic_trace[s]
                self.critic_trace[s] = self.options["gamma"] * self.options["critic_lambda"] * self.critic_trace[s]

            self.V[self.prev_state] = self.V[self.prev_state] + self.options["alpha"] * td_error
            
            
            ''' 
                Actor with trace
            
                1. use V TD error: td_error already obtained
                2. increment actor trace
                3. update actor trace with td_error * trace
                4. update actor 
            '''

            self.actor_trace[self.prev_state][prev_action] += 1
            
            for i, s in enumerate(self.actor_trace):
                for j, a in enumerate(s):
                    self.actor_trace[s][int(a)] = self.options["gamma"] * self.options["actor_lambda"] * self.actor_trace[s][int(a)]
                    
            self.p_a[self.prev_state][prev_action] = self.p_a[self.prev_state][prev_action] + (self.options["beta"] * td_error * self.actor_trace[self.prev_state][prev_action])
            

            
            '''
                softmax
                self.options["temperature"] -- no temperature used in this algorithm (see S&B 1ed, p42)
                
                - see Crites & Barto 1995
                - refactor to use numpy with p=dist: np.random.choice([q_t_0, q_t_1], p=[q_t_0, q_t_1]) [TODO]
            '''
            
            
            
            
            max_element = max(self.p_a[self.prev_state])

            numerator_0 = np.exp(self.p_a[self.prev_state][0] - max_element)
            numerator_1 = np.exp(self.p_a[self.prev_state][1] - max_element)

            # np.exp overflow will be in ER file
            # if this occurs, just carry on, using old values .. but print to stdout (will be in OU file)
            # try catch [TODO]
            
            if np.isinf([numerator_0, numerator_1]).any():
                print(f"out of range in np.exp at {len(agent.action_history)}: {numerator_0}, {numerator_1}")
            else:
                denominator = numerator_0 + numerator_1
                
                self.smv[self.prev_state][0] = numerator_0 / denominator
                self.smv[self.prev_state][1] = numerator_1 / denominator

                

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
        return { "current_state" : self.state, "smv" : copy.deepcopy(self.smv), "p_a" : copy.deepcopy(self.p_a), "V" : copy.deepcopy(self.V), "actor_trace": copy.deepcopy(self.actor_trace), "critic_trace": copy.deepcopy(self.critic_trace) }

       
if __name__ == '__main__':
    print(self.options["name"])