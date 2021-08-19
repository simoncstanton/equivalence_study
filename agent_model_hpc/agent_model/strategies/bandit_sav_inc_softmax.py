#!/usr/bin/env python3
# File: bandit_sav_inc_softmax.py

import random
import numpy as np

from .strategy import Strategy


class Bandit_sav_inc_softmax(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        '''
        RL Method
            Sample Average, non-incremental, softmax
        
        
        '''
        
        self.k_a = [0,0]
        self.q_a = [0,0]
        

    def action(self, agent, previous_step) -> int:
        '''     
            
            
            for each a: Q_n+1 = Q_n + 1/n[R_n - Q_n]
            
            r       : reward at n for a
            n       : count of times action a has been chosen
            
            if n = 0 then Q_n(a) = 0      (or some default)
            
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
                if no previous reward (i.e. this is the first round, then previous_reward == 0
            '''
            r = agent.previous_reward

            # update count for action a
            self.k_a[prev_action] += 1

            
            ''' update q_n for a
            '''
        
            self.q_a[prev_action] = self.q_a[prev_action] + (1/self.k_a[prev_action]) * (r - self.q_a[prev_action]) 

        
        
        '''
            softmax
            
            numerator   : exp(q_t_0/temperature)
            denominator : sum(exp(q_t_0/temperature), exp(q_t_1/temperature))
            sm = numerator / denominator
            if rnd < sm:
                action = 0
            else:
                action = 1
                
            refactor to use numpy: np.random.choice([q_t_0, q_t_1], p=[q_t_0, q_t_1])
        '''

        rnd = random.random()
        
        numerator = np.exp(self.q_a[0]/self.options["temperature"])
        denominator = np.exp(self.q_a[0]/self.options["temperature"]) + np.exp(self.q_a[1]/self.options["temperature"])
        sm = numerator / denominator
        
        if rnd < sm:
            action = 0
        else:
            action = 1
        

        return action



    def get_strategy_internal_state(self):
        return { "k_a" : self.k_a.copy(), "q_a" : self.q_a.copy() }
       
if __name__ == '__main__':
    print(self.options["name"])