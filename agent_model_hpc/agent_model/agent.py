import importlib
#from collections import OrderedDict

class Agent:

    def __init__(self, agent_id, strategy, strategy_options):
        self.agent_id = agent_id
        self.has_state = False
        
        self.action_history = []
        self.reward_history = []
        self.state_history = []
        
        self.total_reward = 0
        self.previous_reward = 0
        
        # opponent_previous_reward - used by SL algorithms ONLY. Updated in trial.py
        self.opponent_previous_reward = 0
        
        # self._m is dynamically loaded strategy module 
        self._m = importlib.import_module('agent_model.strategies.{}'.format(strategy), 'agent_model')
        self.strategy = getattr(self._m, str.capitalize(strategy))(strategy, strategy_options)
        
        
    def step(self, t, previous_step = []):
        action = self.strategy.action(self, previous_step)
        self.action_history.append(action)
        
        if self.strategy.strategy_has_state():
            self.state_history.append(self.strategy.get_strategy_internal_state())
            
        if t > 0:
            self.total_reward += self.previous_reward
            self.reward_history.append(self.previous_reward)

        return action
        
        
    def final_step(self, t, previous_step):
        self.total_reward += self.previous_reward
        self.reward_history.append(self.previous_reward)
    
    
    def agent_has_state(self):
        return self.has_state