#!/usr/bin/env python3
# File: qlearning.py

import random
from random import randint

import copy
from collections import OrderedDict, deque

from .strategy import Strategy


class Qlearning(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        self.state_length = 2 * self.options["memory_depth"] 
        #self.state_space_size = (2 * 2) ** self.options["memory_depth"]

        
        self.memory = deque(maxlen=self.options["memory_depth"])
        self.state = ""
        self.prev_state = ""
        
        ''' Q is {state: values} 
            state is str over action_history length, ie 01010101 (str for 2p ALLC/ALLD, t = 4)
            values are list of two actions: 0: [0], 1: [0]
        '''
        #self.Q = OrderedDict({"": [self.options["optimistic_0"], self.options["optimistic_1"]]})
        self.Q = {"": [self.options["optimistic_0"], self.options["optimistic_1"]]}
        

    def action(self, agent, previous_step) -> int:
        '''
            q       : current q value given previous state and previous action
            alpha   : learning rate
            r       : reward for last action
            gamma   : discount factor
            maxq    : max of q values for current state
            
            prev_state  :    previous state
            prev_action :    previous action
            
            new_q = q + alpha * (r + (gamma * maxq) - q)
            
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
            
            '''
                obtain q value for previous state, action pair
                    type(q) == float
            '''
            q = self.Q[self.prev_state][prev_action]
            
            '''
                obtain reward from last action
                    type(r) == int
                r is stored in agent object as matrix payoff from last action
            '''
            r = agent.previous_reward

            '''
                obtain max q value from actions in current state
                    two lines == torturous,  lambda x should work but haven't got it working yet
            '''

            maxq = max(self.Q[self.state][0], self.Q[self.state][1])          

            
            '''
                calculate new q value 
            '''
            new_q = q + (self.options["alpha"] * (r + (self.options["gamma"] * maxq) - q))
            
            '''
                epsilon policy
            '''
            rnd = random.random()
                
            if rnd > self.options["epsilon"]: # or len(self.memory) > 2000:
                action = self.Q[self.state].index(maxq)
            else:
                action = randint(0,1)

            '''
                update Q table
            '''
            self.Q[self.prev_state][prev_action] = new_q
            
        '''
            push current state into the past
        '''
        self.prev_state = self.state
        

        return action



    def get_strategy_internal_state(self):
        return { "Q" : copy.deepcopy(self.Q) }
       
if __name__ == '__main__':
    print(self.options["name"])