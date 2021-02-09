---
title: "Agent-Based Model of Environmental Migration in Bangladesh"
author: "Kelsea Best"
output: 
  #- html_document
  #- word_document
  - pdf_document
---
# Overview

## Purpose

The purpose of the model is to simulate household migration decisions in
Bangladesh under environmental pressure. The model seeks to understand
how environmental stress in the form of drought and drought-induced
agriculture loss, as well as changing livelihood opportunities, impact
mobility patterns. The initial version of the model uses decision-making
based on utility maximization. Future versions of the model will include
multiple decision-making frameworks. Future versions of the model will
also explore how social networks impact migration decisions through the
exchange of information and resources between origin and destination
locations, including different kinds of destinations.

## Entities, state variables, and scales

This model consists of **individuals** and **household** entities.
Individuals have a gender, age, and employment, as well as a household
that they are assigned to. Households consist of individuals. Other
entities include the **decision class** and **community class**. The
household will access the decision method from the decision class in
order to decide whether or not to send a migrant. Initially, the
decision-making method is a simple utility maximization calculation.
Future versions incorporate Theory of Planned Behavior, Mobility
Potential, and Protection Motivation Theory.

Each household is connected to a **community** entity. In the simple
model, the community represents the origin location. The community has
associated employment opportunities. In a later version of the model,
destination locations will be incorporated as types of community
including Dhaka, Khulna, and another rural location. These destinations
will also have associated employment opportunities that individuals can
assess. Destinations will also have an associated risk and cost to move.
Communities, individuals, and households are all situated within an
environment which will stochastically experience a shock at a given time
step. An environmental shock will impact community opportunities as well
as individual households.

Agents will also keep track of their location where they are residing at
each time step. To represent social networks, agents will be able to
exchange information about migration histories and wealth histories
freely with a random set of other households.

![UML diagram of the model structure](../assets/images/class_diagram.png)

### Global variables

-   `decision` -- decision method to be used to make migration decision
-   `shock_method` -- type of environmental impact simulated, this can be "shock" for a stochastic environmental shock or "slow_onset" for a gradual impact 
-   `mig_util` -- utility to migrate successfully
-   `mig_threshold` -- wealth threshold to migrate
-   `num_hh` -- number of households
-   `num_individuals` -- number of individuals
-   `init_time` -- initialization time (automatically 0)
-   `tick` -- tracks time progression in model
-   `ticks` -- total number of ticks for model to run
-   `migrations` -- tracks overall migrations taken globally
-   `wealth_factor` -- factor to initialize household wealth
-   `ag_factor` -- productivity factor for land that households own
-   `origin_comm` -- origin community (calls community class)
-   `comm_scale` -- proportion of community that is impacted by an environmental shock 
-   `data_set` -- stores data with data\_collect() function
-   `individual_set` -- stores individuals and data
-   `hh_set` -- stores households and data

### Individual class variables

-   `unique_id`
-   `age`
-   `gender` ('M' or 'F')
-   `hh` -- stores idea of household that individual belongs to
-   `employment`
-   `salary`
-   `employer`
-   `can_migrate` --True/ False if inidivdual is eligible to migrate
-   `head` --True/ False if individual is a head of household
-   `migrated` -- True/ False if individual has migrated
-   `wta` -- Salary that individual is willing to accept from a potential employer
    
    
### Household class variables

-   `unique_id`
-   `wealth` -- total wealth in household
-   `hh_size` -- size of household (integer)
-   `individuals` -- data frame that stores individuals that belong to
    that household
-   `head` -- stores individual who is head of household
-   `land_owned` -- value of land owned by household
-   `network`
-   `network_moves`
-   `land_impacted` -- True/False if household's land was impacted by
    environmental shock
-   `wta` -- willing to accept
-   `wtp` -- willing to pay
-   `employees` -- stores employees hired by household
-   `payments` -- stores payments household owes to employees
-   `expenses` -- stores any household expenses
-   `total_utility` -- utility of household summed over individuals
-   `total_util_w_migrant` -- utility if household sends a migrant
-   `num_shocked` -- tracks how many times a household is impacted by an environmental shock
-   `land_prod` -- stores how much wealth a household gains from its land. If a household is not     impacted by a community shock, then this is currently `ag_factor` * `land_owned`. If a           household's land is impacted, then this is zero. 
-   `secure` -- True/False if household has enough wealth to pay for basic food. This represents
    whether or not a household falls beneath a poverty threshold. Currently, this security 
    threshold is based on the World Bank definition of poverty as less than $1.90 USD per person,     per day. 
-   `wellbeing_threshold` -- Calculates the threshold below which a household is not secure.         Based on the World Bank definition of poverty as less than $1.90 USD per person, per day, or     approximately 20,000 BDT per year per member of household.  

### Decision class variables

-   `outcome` -- True/ False for outcome of decision

### Community class variables

-   `impacted` -- True/False if community is impacted by environmental
    shock
-   `scale` -- Percent of community impacted by environmental shock
-   `jobs_avail` -- Number of low-paying non-agricultural jobs available in the community (i.e.     construction, rickshaw driver, etc.). This may decrease if the community is impacted by an environmental shock. 

## Process overview and scheduling

Each simulation starts with creation of a set of individuals,
households, and a community. Individuals are assigned to a household,
and households assign a head of household. These individuals and
households are stored in data frames. Initial individual and household
traits can be set randomly or pre-assigned.

At each step, the origin community will face a probabilistic risk of
drought as an environmental shock, if the "shock_method" is set to "shock",
which will impact agriculture and
employment opportunities. Households will check to see if their land has
been impacted by the environmental shock. Individuals will then update
their eligibility to migrate and then assess employment opportunities
within the community and select an opportunity based on utility and
being able to perform the job (for example, old enough to work in
agriculture and owning land). If the "shock_method" is specified as "slow_onset", then
instead the agricultural productivity of the land in community gradually declines by 
a specified percentage at each step. 

After each individual has selected an employment opportunity within the
community, the household will aggregate utility across individuals and
then, at the household level, the decision to send a migrant or not will
be assessed based on the decision-making method implemented by calling
the decision class. This decision will be recorded. If a household
elects to send a migrant, then that individual will no longer
participate in the ABM but will contribute to the household's wealth at
each step of the model (until later versions in which the agent will go
to a specific destination and later have the option to return-migrate).
Eventually, there will be a probability of the migration failing, in
which case the migrant will not contribute to the household's wealth.
Eventually, households can also decide to move based on exchanging
information and resources across their networks as well as past
experience.

The number of ticks will increase by 1 at each step, and each individual
will age by one year. Data will be collected at each tick and stored in
data\_set.

![Sequence of actions](../assets/images/schedule.png)

# Design concepts

### Basic Principles

This model is based on the literature on environmental migration, which
describes both push and pull factors as being important in migration
decisions, as well as the importance of social networks. The ABM is used
to attempt to reproduce patterns of migration in response to flooding
and drought-induced crop failure in rural Bangladesh (Gray & Mueller,
2012). Three key patterns that are identified in this work are:

-   As the proportion of a community impacted by crop loss increases,
    rates of migration also increase, especially above a threshold of
    approximately 20% of community households impacted. Therefore,
    community-level impacts are important for household migration, and a
    critical threshold may exist.

-   Households that are directly impacted by crop loss are less likely
    to migrate, suggesting that a barrier exists to migrating for more
    vulnerable households.

-   Wealthier households are more likely to migrate.

The decision-making elements of the model are based on behavioral
theories including Theory of Planned Behavior, Protection Motivation
Theory, and Motivation Potential.

### Emergence

Emergence will arise in the form of how rates of migration change
throughout the model run. When specific destination locations are
included, emergence could also provide insights into where migrants will
move and future populations in each destination and origin community. It
is also possible that comparisons across networks of agents will show
that certain networks are more mobile than others, which will be evident
by comparing migration histories.

### Adaptation

Individuals and households adapt to changes in their environment by
changing their livelihood choices as opportunities in the community
change. In later versions of the model, households may also adapt by
updating their beliefs about migration based on past experiences or
experiences of other households within their networks, which in turn
impacts their likelihood of making a migration trip. Sending a migrant
is, of course, another adaptation that households can make.

### Objectives

Agents evaluate an objective based on the decision-making method to
maximize utility, minimize risk, or a combination.

### Learning

Agents will learn both from their own experiences as well as the
experiences of agents in their network.

### Prediction

Agents do not make predictions about the future, but they may consider
risks associated with a decision based on own histories or histories of
other agents in their network.

### Sensing 

Agents are able to sense all of their own traits and the traits in their
current community. They are also able to assess migration histories of
agents in their social network.

### Interaction

Households interact by sharing information about their migration
histories and wealth histories with other households within their
network. Household agents can give and receive information within their
network and make decisions based on this information. Households can
also transfer resources in the form of remittances across their
networks.

### Stochasticity

Stochasticity may be included in the initialization of the model in
terms of agent traits and social network connects. Stochasticity is also
present in the implementation of environmental shock risk at each step.
Stochasticity will be incorporated to determine whether or not a
migration trip was successful, based on a probability of failure.

### Collectives

Households connected by social networks can share information about
their migration experiences with one-another. They can also share
resources.

### Observation

The model records all household migration histories, histories of
environmental impact, and tracks wealth over time. On the larger level,
the model will also track populations in origin and destination
communities over time, total migrations, and the evolution of wealth in
the community.

# Details

## Initialization

Currently, the model is initialized with a number of ticks for the model
to run, number of individual agents, number of household agents, a
decision method to be used, and a migration utility. Agent (household
and individual) traits can be randomly initialized based on a
parameterization from BEMS data.

## Input data

None.

## Submodels

### Model level functions

### Household class functions

* `gather_members`
  Households collect individuals to be in their household. They randomly
  select the number of individuals given by `hh_size` from the individual
  set.

* `assign_head`
  Households assign head of household to the oldest male member of the
  household. If there are no male members, then the oldest female is
  assigned as head of household.

* `check_land`
  Ask households to check to see if their land has been impacted in the
  case of an environmental shock. If a household's land is impacted, then their wealth 
  experiences a stochastic decrease, and their land productivity goes to zero. 

* `migrate`
  Households select a potential migrant from their set of individual
  household members who are eligible to migrate. Households may then
  decide, based on the decision method to send a migrant by calling the
  decision class. If the household does decide to send an individual
  migrant, then `someone_migrated` is increased by 1, and the individual
  no longer participates in the model beyond contributing to household
  wealth.

* `sum_utility`
  The household sums the total utility across all individuals. This is done by asking each 
  individual in the household what his/her salary is, and summing them for the household. Here,    the household also checks if it is secure or not (above poverty threshold), based on the total   earnings. 
  
* `hire_employees`
  If a household's land has not been impacted, then it updates the number of employees that it can hire based on its land owned and its `wtp`. Household updates its `wtp` and `wta`. `wtp` is calculated as the household's `land_productivity` / (`num_employees` + 1). `wta` is calculated as the household's `wellbeing_threshold` / `hh_size`. 

* `update_wealth`
  At the end of each tick, all households update wealth by summing across
  the employment of individuals within the household (or migrants that
  have successfully migrated). Updated wealth is calculated as:
      $$Wealth = PreviousWealth + AllSalaries + LandProductivity - Expenses - PaymentsToEmployees$$ 
  

### Individual class functions 

* `age_up`
  Individuals increase their age by 1 after each tick.

* `check_eligibility`
  Individuals check to see if they are eligible to migrate (currently,
  only male individuals older than 14 years old are eligible).

* `find_work`
  Each individual will look for work within the community. Individuals
  with a large amount of land (representing large land owners)
  may work in agriculture on their own land. If an individual is
  not part of a household with enough of its own land (small land owners or landless), the     individual may seek
  agricultural employment with another household by entering the internal. 
  labor market. If wtp \> wta,
  then the individual may gain employment with another household. If
  supply is not greater than demand, then the agent does not find work in
  agriculture with another household. Individuals who are unable to obtain employment 
  in the labor market may also attempt to seek non-agricultural employment 
  by checking the `avail_jobs` within the community. There are a specified number of jobs tha
  are "skilled" and pay more than "unskilled" non-agricultural jobs. 

### Community class functions 

* `shock`
  Probabilistically experience a drought year based on the annual risk. If
  a drought occurs, then community work opportunities will be updated
  based on a decline in the utility of agriculture.

### Decision class functions

* `decide`
  This part of the model will implement the decision method for households
  to decide whether or not to send a migrant. If the decision conditions
  are achieved, then `outcome` is updated to True.
      + `utility_max` - simple utility maximization
      + `push_threshold` - utility maximization, plus households that are not secure but have sufficient wealth to migrate will send a migrant, representing a last resort option. 

### Model level functions 

* `double_auction`
  Individuals who are looking for employment and households that are looking
  for employees can enter the double auction. Individuals will look for households
  whose `wtp` is greater than their `wta`. If they find such a household, their salary
  will be set as the average between `wtp` and `wta`, and their employer will set to that
  household id. The individual's id will be appended to the household's employer list. 
  The double auction will run for a specified number of rounds or until there are 
  no longer any individuals looking for work or households looking to hire. Individuals who are unable to find employment within the double auction may attempt to take a lower paying, non-agricultural job if there are `avail_jobs` within the community. 
