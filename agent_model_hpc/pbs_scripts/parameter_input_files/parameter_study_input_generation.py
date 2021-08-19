#!/usr/bin/env python3
'''
Parameter Study input generation
usage: python parameter_study_input_generation.py

'''
from numpy import linspace

for i in linspace(0.1, 1, 10):
    for j in linspace(0.1, 1, 10):
        print("{0:.1f}".format(i) + " " + "{0:.1f}".format(j))