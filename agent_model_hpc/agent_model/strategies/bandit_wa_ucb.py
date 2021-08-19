#!/usr/bin/env python3
# File: bandit_wa_ucb.py

import random
import numpy as np

from .strategy import Strategy


class Bandit_wa_ucb(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        '''
        Bandit Method
        Weighted Average, incremental, UCB (Upper-Confidence-Bounds) Action-Selection
        
        
        '''
        self.c = self.options["c"]
        self.q_a = [self.options["optimistic_0"], self.options["optimistic_1"]]
        self.k_a = [1,1]
        

    def action(self, agent, previous_step) -> int:
        '''     
            
            
            for each a: Q_n+1 = Q_n + alpha * [R_n - Q_n]
            
            r       : reward at n for a
            n       : count of times action a has been chosen
            
            if n = 0 then Q_n(a) = 0      (or some default)
            
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
            
            
            ''' update q_n for a
            '''
        
            self.q_a[prev_action] = self.q_a[prev_action] + (self.options["alpha"] * (r - self.q_a[prev_action]))

            # a_0 = self.q_a[0] + self.options["c"] * np.sqrt(np.log(len(agent.action_history)) / self.k_a[0])
            # a_1 = self.q_a[1] + self.options["c"] * np.sqrt(np.log(len(agent.action_history)) / self.k_a[1])
            a_0 = self.q_a[0] + self.c * np.sqrt(np.log(len(agent.action_history)) / self.k_a[0])
            a_1 = self.q_a[1] + self.c * np.sqrt(np.log(len(agent.action_history)) / self.k_a[1])
            action = np.argmax([a_0, a_1])
        
        
        '''
            UCB
        '''
        
        self.k_a[action] += 1


        return action



    def get_strategy_internal_state(self):
        return { "c" : self.c, "q_a" : self.q_a.copy(), "k_a" : self.k_a.copy() }
       
if __name__ == '__main__':
    print(self.options["name"])