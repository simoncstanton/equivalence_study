#!/usr/bin/env python3
# File: bandit_inc_softmax_ap_2ed.py

import random
import numpy as np

import copy
from collections import deque

from .strategy import Strategy


class Bandit_inc_softmax_ap_2ed(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        '''
        Bandit Method
            softmax numerical preference over action probabilities 2ed
        
        
        
        '''

        self.a_p = [0,0]
        self.h_a_0 = 0
        self.h_a_1 = 0
        self.av_r = 0
        self.k = 0
        


    def action(self, agent, previous_step) -> int:
        '''     
            Q_t(a) = r_1 + r_2 + ... + r_k_a / k_a
            
            t       : timestep
            r       : reward at t
            a_p     : action probabilities 
            h_a_0   : preference for action 0
            h_a_1   : preference for action 1
            alpha   : step-size parameter
            av_r    : average of all rewards to present
            
            
            softmax on numerical preference of action (S&B, 2ed, p37)
            
        '''
        super().action(agent, previous_step)
        
        
        ''' first move, action is softmax and is selected at end of method, so nothing to do here '''
        if len(agent.action_history) == 0:
            pass
        
        else:
            prev_action = previous_step[agent.agent_id]

            '''
                obtain reward from last action
                    type(r) == int
                r is stored in agent object as matrix payoff from last action
                if no previous reward (i.e. this is the first round, then last_payoff == 0
            '''
            r = agent.previous_reward

            '''
            if prev_action == 0:
                self.r_k_0.append(r)
            else:
                self.r_k_1.append(r)
                
            self.av_r = sum(self.r_k_0) + sum(self.r_k_1) / (len(agent.history) + 1)
            '''
            
            # update count for action a
            self.k += 1

            
            ''' update q_n for a
            '''
        
            #self.q_a[prev_action] = self.q_a[prev_action] + (1/self.k_a[prev_action]) * (r - self.q_a[prev_action]) 

            
            # softmax on numerical prefs wants average for all rewards from all actions
            self.av_r = self.av_r + (1/self.k) * (r - self.av_r)

            if prev_action == 0:
                self.h_a_0 = self.h_a_0 + self.options["alpha"] * (r - self.av_r) * (1 - self.a_p[0])
                self.h_a_1 = self.h_a_1 - self.options["alpha"] * (r - self.av_r) * self.a_p[1]
            else:
                self.h_a_1 = self.h_a_1 + self.options["alpha"] * (r - self.av_r) * (1 - self.a_p[1])
                self.h_a_0 = self.h_a_0 - self.options["alpha"] * (r - self.av_r) * self.a_p[0]
            

        
        '''
            softmax
            
            numerator   : exp(h_a_0/temperature)
            denominator : sum(exp(h_a_0/temperature), exp(h_a_1/temperature))
            sm = numerator / denominator
            if rnd < sm:
                action = 0
            else:
                action = 1
            
            refactor to use numpy with p=dist: np.random.choice([h_a_0, h_a_1], p=[h_a_0, h_a_1])  [TODO]
        '''

        
        numerator_0 = np.exp(self.h_a_0/self.options["temperature"])
        numerator_1 = np.exp(self.h_a_1/self.options["temperature"])
        denominator = np.exp(self.h_a_0/self.options["temperature"]) + np.exp(self.h_a_1/self.options["temperature"])
        
        self.a_p[0] = numerator_0 / denominator
        self.a_p[1] = numerator_1 / denominator










        rnd = random.random()
        if rnd < self.a_p[0]:
            action = 0
        else:
            action = 1
        
       
        return action


    def get_strategy_internal_state(self):
        return { "a_p" : self.a_p.copy(), "h_a_0" : self.h_a_0, "h_a_1" : self.h_a_1, "av_r" : self.av_r, "k": self.k }
       
if __name__ == '__main__':
    print(self.options["name"])