#!/usr/bin/env python3
# File: sarsa_lambda_replacetrace.py

import random
from random import randint

import copy
from collections import deque

from .strategy import Strategy


class Sarsa_lambda_replacetrace(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        self.state_length = 2 * self.options["memory_depth"]
        '''
        RL method
        TD Lambda, Sutton&Barto 1st edition
        with Replacing Traces (replace-trace)
        
        '''
        
        self.memory = deque(maxlen=self.options["memory_depth"])
        self.state = ""
        self.prev_state = ""
        
        self.Q = {"": [self.options["optimistic_0"], self.options["optimistic_1"]]}
        self.trace = {"": [0, 0]}


    def action(self, agent, previous_step) -> int:
        '''     
            
            
            t       : timestep
            r       : reward at t
            p       : estimated expected average reward
            Q       : state-action value 
            beta    : positive step-size parameter
            alpha   : step-size parameter
            gamma   : discount factor
            
            
            
        '''
        super().action(agent, previous_step)
        
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
             
            r = agent.previous_reward


            # note state
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
            if self.state not in self.Q:
                self.Q[self.state] = [self.options["optimistic_0"], self.options["optimistic_1"]]
            if self.state not in self.trace:
                self.trace[self.state] = [0.0, 0.0]
         
            
            '''
                epsilon policy
            '''
            rnd = random.random()
            maxq = max(self.Q[self.state][0], self.Q[self.state][1])    
            if rnd > self.options["epsilon"]:
                action = self.Q[self.state].index(maxq)
            else:
                action = randint(0,1)

            ''' calc td_error
                    
                td_error = r + (gamma * next_q) - q
            ''' 
            q = self.Q[self.prev_state][prev_action]
            next_q = self.Q[self.state][action]
            
            td_error = r + (self.options["gamma"] * next_q) - q

            
            ''' update eligibility trace for previous state'''
            # not required with replace-trace
            # self.trace[self.prev_state][prev_action] += 1
            

            ''' update Q and trace for all states '''
            for i, s in enumerate(self.Q):

                for j, a in enumerate(s):

                    if s == self.prev_state and int(a) == prev_action:
                        self.trace[s][int(a)] = 1
                    elif s == self.prev_state:
                        self.trace[s][int(a)] = 0
                    else:
                        self.trace[s][int(a)] = self.options["gamma"] * self.options["lambda"] * self.trace[s][int(a)]
                    
                    self.Q[s][int(a)] = self.Q[s][int(a)] + (self.options["alpha"] * td_error * self.trace[s][int(a)])
                    

            
      
        
        # 7. state -> previous_state
        '''
            push current state into the past
        '''
        self.prev_state = self.state
        

        return action


    def get_strategy_internal_state(self):
        return { "Q" : copy.deepcopy(self.Q), "trace" : copy.deepcopy(self.trace) }

       
if __name__ == '__main__':
    print(self.options["name"])