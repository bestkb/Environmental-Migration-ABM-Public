#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Working definition of agent class (household) for ABM
 of environmental migration

@author: kelseabest
"""

#import packages
from decisions import *
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#object class Household
class Household :
    next_uid = 1
    def __init__(self, wealth_factor, ag_factor): #initialize agents
        self.unique_id = Household.next_uid
        Household.next_uid += 1

        #radomly initialize wealth
        self.wealth = random.gauss(wealth_factor, wealth_factor / 5)

        self.hh_size = np.random.poisson(5.13)
        if self.hh_size < 1:
            self.hh_size = 1
        self.individuals = pd.DataFrame() #initialize DF to hold individuals
        self.head = None
        self.land_owned = np.random.normal(14, 5) #np.random.lognormal(4.2, 1) #
        self.secure = True 
        self.wellbeing_threshold = self.hh_size * 20000 #world bank poverty threshold

        #look at these network vars later
        self.network = []
        self.network_moves = 0

        self.someone_migrated = 0
        self.history = []
        self.success = []
        self.land_impacted = False
        self.wta = 0
        self.wtp = 0
        self.num_employees = 0 
        self.employees = []
        self.payments = []
        self.expenses = self.hh_size *20000 #this represents $$ to sustain HH (same as threshold)
        self.total_utility = 0
        self.total_util_w_migrant = 0
        self.num_shocked = 0
        self.ag_factor = ag_factor 
        self.land_prod = self.ag_factor * self.land_owned #productivity from own land 


#assign individuals to a household
    def gather_members(self, individual_set):
        ind_no_hh = individual_set[individual_set['hh'].isnull()]
        if len(ind_no_hh) > self.hh_size:
            self.individuals = pd.concat([self.individuals, ind_no_hh.sample(self.hh_size)])
        else:
            self.individuals = pd.concat([self.individuals, ind_no_hh.sample(len(ind_no_hh))])
        #update information for hh and individual
        self.individuals['ind'].hh = self.unique_id
        individual_set.loc[(individual_set.id.isin(self.individuals['id'])), 'hh'] = self.unique_id
        for i in individual_set.loc[(individual_set.hh == self.unique_id), 'ind']:
            i.hh = self.unique_id
        self.individuals['hh'] = self.unique_id

    def assign_head(self, individual_set):
        my_individuals = individual_set.loc[(individual_set['hh'] == self.unique_id)]
        males = my_individuals[my_individuals['gender']== 'M']
        females = my_individuals[my_individuals['gender']== 'F']
        if (len(males) == 0 and len(females) == 0):
            head_hh = None
            return 
        elif (len(males) != 0):
            head_hh = males[males['age'] == max(males['age'])]
            self.head = head_hh
            head_hh['ind'].head = True
            #replace in individual set
            individual_set.loc[(individual_set.id.isin(head_hh['id'])), 'ind'] = head_hh
        else:
            head_hh = females[females['age'] == max(females['age'])]
            self.head = head_hh
            head_hh['ind'].head = True
            #replace in individual set
            individual_set.loc[(individual_set.id.isin(head_hh['id'])), 'ind'] = head_hh


    def check_land(self, community, comm_scale):
        if community.impacted == True:
            if random.random() < comm_scale:
                self.land_impacted = True
                self.num_shocked += 1
                self.wealth = self.wealth * random.random()
                self.land_prod = 0

    def migrate(self, method, individual_set, mig_util, mig_threshold):
        util_migrate = mig_util #how do I define these?

        my_individuals = individual_set.loc[(individual_set['hh'] == self.unique_id, 'ind')]
        can_migrate = []
        for i in my_individuals:
            if i.can_migrate == True and i.migrated == False:
                can_migrate.append(i)
        if len(can_migrate) != 0:
            migrant = np.random.choice(can_migrate, 1)
        else:
            return

        if method == 'utility' and self.wealth > mig_threshold:
            self.total_util_w_migrant = self.total_utility - migrant[0].salary + util_migrate 
            decision = utility_max()
            decision.decide(self)
            if decision.outcome == True:
                self.wealth = self.wealth - mig_threshold #subtract out mig_threshold cost
                self.someone_migrated += 1
                migrant[0].migrated = True
                migrant[0].salary = util_migrate
                individual_set.loc[(individual_set.id == migrant[0].unique_id), 'ind'] = migrant[0]

        if method == 'push_threshold' and self.wealth > mig_threshold:
            self.total_util_w_migrant = self.total_utility - migrant[0].salary + util_migrate 
            decision = push_threshold()
            decision.decide(self)
            if decision.outcome == True:
                self.wealth = self.wealth - mig_threshold #subtract out mig_threshold cost
                self.someone_migrated += 1
                migrant[0].migrated = True
                migrant[0].salary = util_migrate
                individual_set.loc[(individual_set.id == migrant[0].unique_id), 'ind'] = migrant[0]

        else:
            pass

    
    def sum_utility(self, individual_set):
        my_individuals = individual_set.loc[(individual_set['hh'] == self.unique_id, 'ind')]
        sum_util = 0
        for i in my_individuals:
            sum_util = sum_util + i.salary
        self.total_utility = sum_util

        if self.total_utility < self.wellbeing_threshold:
            self.secure = False
        else:
            self.secure = True 

    def hire_employees(self): #how many people to hire? and wtp 
        if self.land_impacted == False:
            self.num_employees = round(self.land_owned / 2)
        else:
            self.num_employees = 0 

        if self.num_employees > 0: 
            self.wtp = ((self.ag_factor * self.land_owned) / (self.num_employees + 1))
            self.wta = (self.wellbeing_threshold / self.hh_size) * random.random() 
        else:
            self.wtp = 0
            self.wta = (self.wellbeing_threshold / self.hh_size) * random.random()


    def update_wealth(self, individual_set):
        #update wealth here
        my_individuals = individual_set.loc[(individual_set['hh'] == self.unique_id, 'ind')]
        sum_salaries = 0  
        #sum across all salaries 
        for i in my_individuals:
            sum_salaries = sum_salaries + i.salary
        
        self.wealth = self.wealth + sum_salaries - self.expenses - np.sum(self.payments) + self.land_prod
        
        if self.wealth < 0:
            self.wealth = 0 
            self.secure = False 

        #reset these values
        self.land_impacted = False
        self.land_prod = self.ag_factor * self.land_owned
        self.employees = []



#####################################################################
#to work on these later
    def set_network(self, agent_set, network_structure, network_size):
        if network_structure == 'random':
            self.network = agent_set.sample(network_size)
            for a in self.network:
                a.network.append(self) #add self to other person's network

    def check_network(self):
        for a in self.network:
            if a.someone_migrated == 1:
                self.network_moves += 1
