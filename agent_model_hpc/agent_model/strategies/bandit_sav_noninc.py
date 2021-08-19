#!/usr/bin/env python3
# File: bandit_sav_noninc.py

import random
from random import randint

from .strategy import Strategy


class Bandit_sav_noninc(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        '''
        Bandit Method
            Sample Average, non-incremental, e-greedy
        
        
        '''

        self.k_a = [0,0]
        self.k_a_0 = 0  # sum
        self.k_a_1 = 0  # sum
        #self.r_k_0 = []
        #self.r_k_1 = []
        

    def action(self, agent, previous_step) -> int:
        '''     
            Q_t(a) = r_1 + r_2 + ... + r_k_a / k_a
            
            t       : timestep
            r       : reward at t
            k_a     : count of times action a has been chosen
            
            if k_a = 0 then Q_t(a) = 0      (or some default)
            
            
            q_t     : estimated value at time t
            
        '''
        super().action(agent, previous_step)
        
        q_t_0 = 0
        q_t_1 = 0
        
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
            
            
            ''' append reward for action k to self.r_k_n
            '''
            if prev_action == 0:
                #self.r_k_0.append(r)
                self.k_a_0 += r
            else:
                #self.r_k_1.append(r)
                self.k_a_1 += r
        
            self.k_a[prev_action] += 1

            
            # k_a_0_sum = sum(r_k_0)
            # k_a_1_sum = sum(r_k_1)
            #self.k_a_1_sum += self.r_k_1
            

            
            if self.k_a[0] != 0:
                q_t_0 = self.k_a_0 / self.k_a[0]

            if self.k_a[1] != 0:
                q_t_1 = self.k_a_1 / self.k_a[1]

        
        q_t_a = max([q_t_0, q_t_1])
        q_t_a = [q_t_0, q_t_1].index(q_t_a)

        
        
        '''
            epsilon policy
        '''
        rnd = random.random()
        
        if rnd > self.options["epsilon"]: 
            action = q_t_a
        else:
            action = randint(0,1)
        
        
        return action



    def get_strategy_internal_state(self):
        return { "k_a" : self.k_a.copy(), "k_a_0" : self.k_a_0, "k_a_1" : self.k_a_1 }
       
if __name__ == '__main__':
    print(self.options["name"])