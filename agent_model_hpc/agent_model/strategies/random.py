#!/usr/bin/env python3
# File: random.py

from random import randint
from .strategy import Strategy

class Random(Strategy):
    
    def __init__(self, strategy, strategy_options):
        super().__init__(strategy, strategy_options)
        
        
    def action(self, player, previous_round) -> int:
        super().action(player, previous_round)        
        return randint(0, 1)



if __name__ == '__main__':
    print(self.options["name"])