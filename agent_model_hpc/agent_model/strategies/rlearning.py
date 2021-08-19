#!/usr/bin/env python3
# File: rlearning.py

import random
from random import randint

import copy
from collections import deque

from .strategy import Strategy


class Rlearning(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        self.state_length = 2 * self.options["memory_depth"]
        '''
        RL method
        R-Learning, Sutton&Barto 1st edition
        
        '''
        
        self.memory = deque(maxlen=self.options["memory_depth"])
        self.state = ""
        self.prev_state = ""
        
        # 1 initialise p, Q arbitrarily
        self.p = 0

        self.Q = {"": [self.options["optimistic_0"], self.options["optimistic_1"]]}
        

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
         
            
            # 4 calc transient
            '''
                transient = alpha * (r - p + maxq_next - q)
            ''' 
            q = self.Q[self.prev_state][prev_action]
            maxq = max(self.Q[self.prev_state][0], self.Q[self.prev_state][1])
            maxq_next = max(self.Q[self.state][0], self.Q[self.state][1])
            
            transient = self.options["alpha"] * (r - self.p + maxq_next - q)

            
            # 5 update Q
            self.Q[self.prev_state][prev_action] += transient
            
            # 6. update p
            if q == maxq:
                self.p = self.p + (self.options["beta"] * (r - self.p + maxq_next - maxq))
          

            
            '''
                epsilon policy
            '''
            rnd = random.random()
            maxq = max(self.Q[self.state][0], self.Q[self.state][1])    
            if rnd > self.options["epsilon"]:
                action = self.Q[self.state].index(maxq)
            else:
                action = randint(0,1)
      
        
        # 7. state -> previous_state
        '''
            push current state into the past
        '''
        self.prev_state = self.state
        
        return action



    def get_strategy_internal_state(self):
        return { "Q" : copy.deepcopy(self.Q), "p" : self.p }
       
if __name__ == '__main__':
    print(self.options["name"])