#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working definition of decision class for ABM
 of environmental migration

@author: kelseabest
"""

#import packages
import random
import math
import numpy as np
import matplotlib.pyplot as plt

class decision :
    #method decide returns True or False
    #subclass of decisions
    def __init__(self): #initialize outcome
        self.outcome = False
    def decide(self):
        pass

class utility_max(decision):
    def __init__(self): #initialize utilities
        super().__init__()
    def decide(self, household):
        if household.total_utility < household.total_util_w_migrant:
            self.outcome = True
