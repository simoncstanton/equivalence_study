#!/usr/bin/env python3
# File: watkins_q_lfa.py

import os

import random
from random import randint

import copy
from collections import deque
import numpy as np

from .strategy import Strategy


class Watkins_q_lfa(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        self.state_length = 2 * self.options["memory_depth"]
        '''
        RL method
        Watkins Linear Function Approximation, Sutton&Barto 1st edition
            with binary features, e-greedy policy, accumulating traces
        
        '''
        
        self.memory = deque(maxlen=self.options["memory_depth"])
        self.state = None
        self.prev_state = None
        
        self.weights_initial = 0
        
        self.features = self.get_feature_vector()
        
        self.weights = [self.weights_initial for i in self.features]
        #print(os.path.basename(__file__) + ":: features at instantiation", self.features)
        #print(os.path.basename(__file__) + ":: weights at instantiation", self.weights)

        
        self.actions = [0,1]
        
        self.qs = list(np.dot(self.get_feature_vector(self.state, i), self.weights) for i in self.actions)
        #print(self.qs)
        self.get_maximal_action(self.qs)
      

    def action(self, agent, previous_step) -> int:
        '''     
            
            
            t       : timestep
            r       : reward at t
            
            
            
        '''
        super().action(agent, previous_step)
        
        #print("previous_step:", previous_step)
        
        ''' first move, act according to distribution supplied by option '''
        if len(agent.action_history) == 0:
            rnd = random.random()
            if rnd > (1 - self.options["initial_action"]):
                action = 1
            else:
                action = 0
        
        else:
            # agent_id maps to the uple position to get that (this) agent's action out of the __previous_step__ data structure (which is a tuple)
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
            
            
            
            
            self.qs = list(np.dot(self.get_feature_vector(self.prev_state, i), self.weights) for i in self.actions)
            
            '''
                epsilon policy
            '''
            rnd = random.random() 
            if rnd > self.options["epsilon"]: 
                action = self.get_maximal_action(self.qs)
                #print("features", self.features)
                #print("weights", self.weights)
                #print("epsilon", action)
            else:
                action = randint(0,1)
            
            
            # 
            phi = self.get_feature_vector(self.prev_state, prev_action)
            prev_q = np.dot(phi, self.weights)
            #print("phi", phi)
            #print("prev_q", prev_q)
            
            phi_next = self.get_feature_vector(self.state, action)
            next_q = np.dot(phi_next, self.weights)
            #print("next phi", phi_next)
            #print("next_qs", next_q)
            
            td_error = r + (self.options["gamma"] * next_q) - prev_q
            #print("td_error", td_error)
            
            for i in range(len(self.weights)):
                self.weights[i] += self.options["alpha"] * td_error * phi_next[i]
                
            #print("self.weights", self.weights)
            
            

            
      
        
        # 7. state -> previous_state
        '''
            push current state into the past
        '''
        self.prev_state = self.state
        
        #print("agent_id, action:", agent.agent_id, action)
        #print()
        return action

    def get_maximal_action(self, q_a):
        #print("q_a", q_a)
        maxq = max(q_a)
        #print("index",  q_a.index(maxq))
        return q_a.index(maxq)
        
    def get_feature_vector(self, state=None, action=None):
    
        # artint.info/html/ArtInt_272.html 
        #   w_0 shoud always be 1.
        
        if state == None and action == None:
            return [1, 1, 1, 1, 1]
        
        f1 = 1 if state == '00' and action == 0 else 0 # CC, C
        f2 = 1 if state == '01' and action == 0 else 0 # CD, C
        f3 = 1 if state == '10' and action == 1 else 0 # DC, D
        f4 = 1 if state == '11' and action == 1 else 0 # DD, D
        
        
        self.features = [1, f1, f2, f3, f4]
        return self.features


    def get_strategy_internal_state(self):
        return { "state" : self.state, "f" : self.features.copy() }  # , "weights" : copy.deepcopy(self.weights)
       
if __name__ == '__main__':
    print(self.options["name"])