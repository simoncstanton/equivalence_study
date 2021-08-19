#!/usr/bin/env python3
# File: bandit_sl_direct.py

import random
import numpy as np

from .strategy import Strategy


class Bandit_sl_direct(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        '''
        Bandit method
            supervised learning direct method S&B 1ed p33
        
        
        '''
        self.a = [0,0]
        

    def action(self, agent, previous_step) -> int:
        

        '''     
            
            
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

            
            ''' assess own payoff v opponent payoff 
            PD:         COL:
                        C       D
            ROW:    C   3,3     0,5
                    D   5,0     1,1
            
            scalar:     self.matrix = [(3,3),(0,5)],[(5,0),(1,1)]
            '''

            
            r = agent.previous_reward
            r_opp = agent.opponent_previous_reward



            (p0, p1) = self.options["gameform_matrix"][previous_step[0]][previous_step[1]]



                
            if agent.agent_id == 0:
                # choice between rows - Up or Down. So want values of index 0 in col that P2 played.
                
                (alt_p0, alt_p1) = self.options["gameform_matrix"][np.logical_not(previous_step[0]).astype(int)][previous_step[1]] 

                
                if alt_p0 > p0:
                    self.a[np.logical_not(prev_action).astype(int)] += 1
                else:
                    self.a[prev_action] += 1
                
                    
            if agent.agent_id == 1:
                # choice between cols - Left or Right. So want values of index 1 in row that P1 played.
                                
                (alt_p0, alt_p1) = self.options["gameform_matrix"][previous_step[0]][np.logical_not(previous_step[1]).astype(int)]

                
                if alt_p1 > p1:
                    self.a[np.logical_not(prev_action).astype(int)] += 1
                else:
                    self.a[prev_action] += 1
                

            
            max_a = max(self.a)
            action = self.a.index(max_a)

            
        return action



    def get_strategy_internal_state(self):
        return { "a" : self.a.copy() }
       
if __name__ == '__main__':
    print(self.options["name"])