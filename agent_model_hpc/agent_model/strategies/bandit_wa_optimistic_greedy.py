#!/usr/bin/env python3
# File: bandit_wa_optimistic_greedy.py

import random

from .strategy import Strategy


class Bandit_wa_optimistic_greedy(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)
        
        '''
        Bandit Method
        Weighted Average, incremental, e-greedy
        
        
        '''
        
        self.q_a = [self.options["optimistic_0"], self.options["optimistic_1"]]
        
    

    def action(self, agent, previous_step) -> int:
        '''     
            
            
            for each a: Q_n+1 = Q_n + alpha * [R_n - Q_n]
            
            r       : reward at n for a
            n       : count of times action a has been chosen
            
            if n = 0 then Q_n(a) = 0      (or some default)
            
        '''
        super().action(agent, previous_step)
        
        ''' first move, action is greedy and is selected at end of method, so nothing to do here '''
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

            
            ''' update q_n for a
            '''
        
            self.q_a[prev_action] = self.q_a[prev_action] + (self.options["alpha"] * (r - self.q_a[prev_action]))
      

        max_q_a = max(self.q_a)
        index_q_a = self.q_a.index(max_q_a)

        
        '''
            greedy policy
        '''
        

        action = index_q_a
        

        return action



    def get_strategy_internal_state(self):
        return { "q_a" : self.q_a.copy() }
        
if __name__ == '__main__':
    print(self.options["name"])