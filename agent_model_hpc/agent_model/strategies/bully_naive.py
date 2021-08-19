#!/usr/bin/env python3
'''
    bully_naive.py
    
    Strategy:
        - initial action is to 'defect'
        - therafter, action is the opposite of the opponent's last action
        
    Parameters:
        - name: bully_naive
        - memory_depth: 1
        - has_state: False
        
'''

from .strategy import Strategy
import numpy as np

class Bully_naive(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
    def action(self, agent, previous_step) -> int:
        super().action(agent, previous_step)
        
        choice = 1
        if agent.action_history:
            if previous_step[np.logical_not(agent.agent_id).astype(int)] == 1:
                choice = 0
           
        return choice



if __name__ == '__main__':
    print(self.options["name"])