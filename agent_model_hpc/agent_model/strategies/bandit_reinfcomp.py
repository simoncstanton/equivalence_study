#!/usr/bin/env python3
# File: bandit_reinfcomp.py

import random
import numpy as np

from .strategy import Strategy


class Bandit_reinfcomp(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)
        
        '''
        Bandit Method
            Reinforcement Comparison, softmax on preference 1ed
        
        
        
        '''

        self.a_p = [0,0]
        self.p_a = [0,0]
        self.ref_reward = self.options["ref_reward"] # instance variable for mutability and readability in self.action()
        


    def action(self, agent, previous_step) -> int:
        '''     
            
            
            t       : timestep
            r       : reward at t
            a_p     : action probabilities 
            p_a     : preference for actions
            beta    : positive step-size parameter
            alpha   : step-size parameter
            ref_r   : reference reward
            
            
            softmax on numerical preference of action (S&B, 2ed, p37)
            
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


            
            # update preferences for actions
            self.p_a[prev_action] = self.p_a[prev_action] + (self.options["beta"] * (r - self.ref_reward))
            
            
            # update reference reward
            self.ref_reward = self.ref_reward + (self.options["alpha"] * (r - self.ref_reward))
          

            
            '''
                softmax
                self.options["temperature"] -- no temperature used in this algorithm (see S&B 1ed, p42)
                
                BUT, seee Crites & Barto 1995
                    refactor to use numpy with p=dist: np.random.choice([q_t_0, q_t_1], p=[q_t_0, q_t_1]) [TODO?]
            '''

            
            numerator_0 = np.exp(self.p_a[0])
            numerator_1 = np.exp(self.p_a[1])
            denominator = np.exp(self.p_a[0]) + np.exp(self.p_a[1])
            
            self.a_p[0] = numerator_0 / denominator
            self.a_p[1] = numerator_1 / denominator

            rnd = random.random()
            if rnd < self.a_p[0]:
                action = 0
            else:
                action = 1
            

        return action



    def get_strategy_internal_state(self):
        return { "a_p" : self.a_p.copy(), "p_a" : self.p_a.copy(), "ref_reward" : self.ref_reward }
       
if __name__ == '__main__':
    print(self.options["name"])