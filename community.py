#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working definition of community class for ABM
 of environmental migration

@author: kelseabest
"""

#import packages
import random
import math
import numpy as np
import matplotlib.pyplot as plt

class community :
    def __init__(self, n_hh, n_jobs, comm_impact):
        self.impacted = False
        self.n_hh = n_hh   
        self.avail_jobs = n_jobs
        self.comm_impact = comm_impact
    #environmental shock
    def shock(self):
        if random.random() < 0.2:
            self.impacted = True
            self.avail_jobs = self.avail_jobs * (1 - self.comm_impact)  #number of jobs decreases with scale of community impact
            #self.scale = random.random()

#origin community
class origin(community):
    def __init__(self, n_hh, n_jobs, comm_impact):
        super(origin, self).__init__(n_hh, n_jobs, comm_impact)
    def shock(self):
        super(origin, self).shock()

#destinations
class dhaka(community):
    def __init__(self):
        super().__init__()

class khulna(community):
    def __init__(self):
        super().__init__()

class rural(community):
    def __init__(self):
        super().__init__()
