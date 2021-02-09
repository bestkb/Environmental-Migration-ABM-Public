#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is the actual model with scheduling and steps for
 ABM of environmental migration

@author: kelseabest
"""

#import packages
from individual import *
from community import *
from decisions import *
from hh_class import *
import random
import math
import numpy as np
import pandas as pd

#initialize model
class ABM_Model:
    def __init__(self, ticks, N_hh, N_ind, decision, mig_util, mig_threshold, wealth_factor, ag_factor, comm_scale, shock_method, jobs_avail):
        self.decision = decision #set decision type
        self.mig_util = mig_util #utility to migrate
        self.mig_threshold = mig_threshold #threshold to migrate
        #self.network_structure = network_structure
        self.num_hh = N_hh #households
        self.num_individuals = N_ind #number of individuals
        init_time = 0 #init ticks to 0 
        self.tick = init_time
        self.ticks = ticks #number of ticks for model to run
        self.migrations = pd.DataFrame()#Initialize number of overall migrations
        self.wealth_factor = wealth_factor #scale of initial household wealth
        self.ag_factor = ag_factor #scalar of relationship between land and wealth
        self.comm_scale = comm_scale #scale (% community) impacted by an environmental shock
        self.shock_method = shock_method #this can be "shock" or "slow_onset"
        self.jobs_avail = jobs_avail #number of non_ag jobs in community 

        #create community and initialize opportunities
        self.origin_comm = origin(self.num_hh, self.jobs_avail, self.comm_scale)

        #for storing data
        self.data_set = pd.DataFrame()
        self.last = pd.DataFrame()
        self.got_job = 0 #tracks successful job in labor market

        #create individuals
        self.individual_set = pd.DataFrame()
        for i in range(self.num_individuals):
            ind = Individual(self.ag_factor)
            row = pd.DataFrame({'ind': [ind], 'id': [ind.unique_id],
                                'age': [ind.age], 'hh': [ind.hh],
                               'gender': [ind.gender]})
            self.individual_set = pd.concat([self.individual_set, row])

        # Create households
        self.hh_set = pd.DataFrame() #empty list to store agents created
        for i in range(self.num_hh):
            a = Household(self.wealth_factor, self.ag_factor)
            a.gather_members(self.individual_set)
            a.assign_head(self.individual_set)
            #a.set_network()
            row = pd.DataFrame({'household': [a], 'hh_id': [a.unique_id],
                                            'wtp': [a.wtp],
                                           'wta': [a.wta]})
            self.hh_set = pd.concat([self.hh_set, row])

    def model_step(self): #model step does each

            #random schedule each time
        random_sched_hh = np.random.permutation(range(1, self.num_hh+ 1))
        random_sched_ind = np.random.permutation(range(1, self.num_individuals+ 1))

            #environmental shock in origin
        if self.shock_method == "shock":
            self.origin_comm.shock()
        else: 
            self.ag_factor = self.ag_factor * 0.95 #5% decrease in productivitiy each step 

            #households need to check land
        for i in random_sched_hh: #these are the steps at each tick for hh
            agent_var = self.hh_set[self.hh_set.hh_id == i].household
            agent_var[0].check_land(self.origin_comm, self.comm_scale)
            agent_var[0].hire_employees()

            #individuals look for work
        for j in random_sched_ind: #steps for individuals
            ind_var = self.individual_set[self.individual_set.id == j].ind
            ind_var[0].check_eligibility()
            ind_var[0].find_work(self.hh_set, self.mig_util)

        #double auction at model level 
        self.double_auction()

            #households decide to send a migrant or not and update wealth
        for i in random_sched_hh: #these are the steps at each tick for hh
            agent_var = self.hh_set[self.hh_set.hh_id == i].household
            #agent_var.check_network()
            agent_var[0].sum_utility(self.individual_set)
            agent_var[0].migrate(self.decision, self.individual_set, self.mig_util, self.mig_threshold)
            agent_var[0].update_wealth(self.individual_set)


    def double_auction(self): #gets people looking for work and hh employing
        poss_employees = []  
        poss_employers = [] 
        still_looking_skilled = []
        still_looking_unskilled = []
        auctions = 3 # rounds w/ nothing changing 
        static_rounds = 0 

        for i in self.individual_set['ind']:
            if i.employment == "Looking":
                poss_employees.append(i)
        if poss_employees == None:
            return
        for h in self.hh_set['household']:
            if h.num_employees > 0:
                poss_employers.append(h)
        if poss_employers == None:
            return 

        all_looking = len(poss_employees)
        
        while static_rounds < auctions and all_looking > 0: 
            changed = False 
            for a in poss_employers: #households pick some people
                if a.num_employees > 0: 
                    if a.num_employees > len(poss_employees):
                        random_inds_look =  np.random.choice(poss_employees, len(poss_employees))
                    else:
                        random_inds_look =  np.random.choice(poss_employees, a.num_employees)
                    for random_ind in random_inds_look:
                        if random_ind.employment != "Looking":
                            pass 
                        elif a.wtp >= random_ind.wta:
                            a.employees.append(a)
                            a.num_employees = a.num_employees - 1
                            random_ind.salary = (random_ind.wta + a.wtp)/2
                            random_ind.employment = "OtherAg"
                            changed = True 
                            random_ind.employer = a.unique_id
                            a.payments.append(random_ind.salary)
                            all_looking = all_looking - 1 
                            self.got_job += 1 
                            self.individual_set.loc[(self.individual_set.id == random_ind.unique_id), 'ind'] = random_ind
                self.hh_set.loc[(self.hh_set.hh_id == a.unique_id), 'household'] = a
            if changed:
                static_rounds = 0 
            else:
                static_rounds += 1 

        #individuals may look for an unskilled or a skilled job within the community 
        for i in self.individual_set['ind']:
            if i.employment == "Looking":
                my_hh = self.hh_set[self.hh_set['hh_id'] == i.hh]['household']
                if my_hh[0].wealth > self.wealth_factor:
                    still_looking_skilled.append(i)
                else:
                    still_looking_unskilled.append(i)
        if still_looking_unskilled == None and still_looking_skilled == None:
            return 
        if len(still_looking_unskilled) > self.origin_comm.avail_jobs / 2:
            found_other_job_unskilled = random.sample(still_looking_unskilled, round(self.origin_comm.avail_jobs / 2))
        else:
            found_other_job_unskilled = still_looking_unskilled

        if len(still_looking_skilled) > self.origin_comm.avail_jobs / 2:
            found_other_job_skilled = random.sample(still_looking_skilled, round(self.origin_comm.avail_jobs / 2))
        else:
            found_other_job_skilled = still_looking_skilled

        for i in found_other_job_unskilled:
            i.employment = "OtherNonAg_Unskilled"
            i.salary = 24000 * random.random() #some small number
            self.individual_set.loc[(self.individual_set.id == i.unique_id), 'ind'] = i

        for i in found_other_job_skilled:
            i.employment = "OtherNonAg_Skilled"
            i.salary = 50000 * random.random() #some greater number
            self.individual_set.loc[(self.individual_set.id == i.unique_id), 'ind'] = i

                   
    def data_collect(self): #use this to collect model level data
    #household level data
        for j in range(1, self.num_hh + 1):
            hh_var = self.hh_set[self.hh_set.hh_id == j].household
            hh = hh_var[0]
            row = pd.DataFrame({'hh_id': [hh.unique_id], 'migrations': [hh.someone_migrated],
                                'wealth': [hh.wealth], 'num_shocked':[hh.num_shocked], 
                                'wtp': [hh.wtp], 'wta': [hh.wta], 'found_work': [self.got_job], 
                                'tick': [self.tick], 'ag_fac': [self.ag_factor],
                                'mig_util':[self.mig_util], 'mig_threshold':[self.mig_threshold],
                                'comm_scale':self.comm_scale})
            self.data_set = pd.concat([self.data_set, row])


        self.last = self.data_set[self.data_set['tick'] == self.tick]
        mig_sum = self.last.iloc[:,1].sum(axis=0)
        row = pd.DataFrame({'tick': [self.tick], 'total_mig': [mig_sum]})
        self.migrations = pd.concat([self.migrations, row])

    #tick up model 
    def tick_up(self):
        #tick and reset key values
        self.tick += 1
        self.origin_comm.impacted = False
        self.origin_comm.avail_jobs = self.jobs_avail 

        #age everyone 1 year
        for j in range(1, self.num_individuals + 1):
            ind_var = self.individual_set[self.individual_set.id == j].ind
            ind_var[0].age_up()
