#!/usr/bin/env python3
# File: fictitiousplay.py

import random
import numpy as np

from .strategy import Strategy



class Fictitiousplay(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)
        
        self.step = 0
        self.opponent_counts = [0,0]
        self.best_rewards_0 = [0, 0]
        self.best_rewards_1 = [0, 0]

    def action(self, agent, previous_step) -> int:
       
        super().action(agent, previous_step)

        
        ''' first move, act according to distribution supplied by option '''
        if len(agent.action_history) == 0:
            rnd = random.random()
            if rnd > (1 - self.options["initial_action"]):
                action = 1
            else:
                action = 0
 
        else:
            action = 1
            r = agent.previous_reward
            
            if previous_step[np.logical_not(agent.agent_id).astype(int)] == 0:
                if self.best_rewards_0[previous_step[agent.agent_id]] < r:
                    self.best_rewards_0[previous_step[agent.agent_id]] = r
            else:
                if self.best_rewards_1[previous_step[agent.agent_id]] < r:
                    self.best_rewards_1[previous_step[agent.agent_id]] = r
            
            
            self.opponent_counts[previous_step[np.logical_not(agent.agent_id).astype(int)]] += 1

            
            belief_0 = self.opponent_counts[0] / self.step
            belief_1 = self.opponent_counts[1] / self.step

            
            if belief_0 >= belief_1:
                if self.best_rewards_0[0] > self.best_rewards_1[0]:
                    action = 0
                else:
                    action = 1
            else:
                if self.best_rewards_0[1] > self.best_rewards_1[1]:
                    action = 0
                else:
                    action = 1
                    
            
        self.step += 1
        
        return action


   
    def get_strategy_internal_state(self):
        return { "step" : self.step, "opp" : self.opponent_counts.copy(), "br_0" : self.best_rewards_0.copy(), "br_1" : self.best_rewards_1.copy() }

       
if __name__ == '__main__':
    print(self.options["name"])