#!/usr/bin/env python3
# File: bandit_pursuit_sav.py

import random
import numpy as np

from .strategy import Strategy


class Bandit_pursuit_sav(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)

        
        '''
        Bandit Method
            Reinforcement Comparison, softmax on preference 1ed
        
        
        
        '''

        self.a_p = [0.5, 0.5]
        self.q_a = [self.options["optimistic_0"], self.options["optimistic_1"]]
        self.k_a = [0, 0]
 
        

    def action(self, agent, previous_step) -> int:
        '''     
            
            
            t       : timestep
            r       : reward at t
            a_p     : action probabilities / preferences
            q_a     : action-value estimates for actions
            beta    : positive step-size parameter 
            
            
            
            softmax on numerical preference of action (S&B, 2ed, p37)
            
        '''
        super().action(agent, previous_step)
        
        ''' first move, action is from action preferences and is selected at end of method, so nothing to do here '''
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



            ''' update action-value estimates
                sample-average
            '''
            # update count for action a
            self.k_a[prev_action] += 1

            
            # update q_n for a
            self.q_a[prev_action] = self.q_a[prev_action] + ((1/self.k_a[prev_action]) * (r - self.q_a[prev_action])) 

          
          
            '''
                determine next t max action-value
            '''
            a_t = np.argmax(self.q_a)
            a_alt = np.logical_not(a_t).astype(int)

            
            # update action preferences
            self.a_p[a_t] = self.a_p[a_t] + (self.options["beta"] * (1 - self.a_p[a_t]))
            self.a_p[a_alt] = self.a_p[a_alt] + (self.options["beta"] * (0 - self.a_p[a_alt]))

            

        
        '''
            action is selected from preference distribution
        '''
        rnd = random.random()

        if rnd < self.a_p[0]:
            action = 0
        else:
            action = 1
            
        
        return action



    def get_strategy_internal_state(self):
        return { "a_p" : self.a_p.copy(), "q_a" : self.q_a.copy(), "k_a" : self.k_a.copy() }
       
if __name__ == '__main__':
    print(self.options["name"])