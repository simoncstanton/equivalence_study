#!/usr/bin/env python3
# File: strategy_abc.py

from abc import ABC, abstractmethod

class Strategy(ABC):
    
    def __init__(self, name, strategy_options):
        super().__init__()
        self.options = {
            "name":    "superclass placeholder",
            "has_state": False,
        }
        self.set_options(name, strategy_options)
    
    
    def action(self, agent, previous_step) -> int:
        pass
     
    
    def set_options(self, name, strategy_options):
        self.options['name'] = name
        self.options.update(strategy_options)


    def print_options(self, verbose = False):
        if verbose:
            [print('{: <14}{}'.format(key, value)) for key, value in self.options.items()]
        else: 
            [print('{: <14}{}'.format(key, value)) for key, value in self.options.items() if self.options[key]]        

    def name(self):
        return self.name
        
    def memory_to_state_key(self):
        state = ""
        for i in reversed(self.memory):
            if len(state) < self.state_length:
                for k in i:
                    state += str(k)
        return state
        
    def strategy_has_state(self):
        return self.options["has_state"]
     
    def get_strategy_internal_state(self):
        pass

