from pyomo.environ import *
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy
from pyomo.opt import SolverFactory

model = ConcreteModel()

# DATA
countries = ['DE', 'DK', 'SE']
techs = ['Wind', 'PV', 'Gas', 'Hydro', 'Battery', 'Nuclear']
efficiency = {'Wind' : 1, 'PV' : 1, 'Gas' : 0.4, 'Hydro' : 1, 'Battery' : 0.9, 'Nuclear' : 0.4} #you could also formulate eta as a time series with the capacity factors for PV and wind

def annualizedCost(InvestmentCost, expectedLifetime):
    discountRate = 0.05
    return InvestmentCost * ( discountRate / ( 1 - ( 1 / ( 1 + discountRate ) ** expectedLifetime )))

input_data = pd.read_csv('data/TimeSeries.csv', header=[0], index_col=[0])


#TIME SERIES HANDLING
def demandData():
    demand = {}
    for n in model.nodes:
        for t in model.time:
            demand[n,t] = float(input_data.iloc[t]["Load_" + n])
    return demand



#SETS
model.nodes = Set(initialize = countries, doc='countries')
model.time = Set(initialize = input_data.index, doc='hours')
model.gens = Set(initialize = techs, doc='generators')


#PARAMETERS
model.demand = Param(model.nodes, model.time, initialize=demandData())
model.efficiency = Param(model.gens, initialize=efficiency, doc='Conversion efficiency')


#VARIABLES
capMaxdata = pd.read_csv('data/capMax.csv', header=[0,1], index_col=[0])

batteryOn = False

def capacity_max(model, n, g):
    capMax = {}
    if g in capMaxdata.columns:
        capMax[n, g] = float(capMaxdata[g].loc[capMaxdata.index == n])
        return 0.0, capMax[n,g]
    elif g == 'Battery' and not batteryOn:
        return 0.0, 0.0
    else:
        return 0.0, None

model.capa = Var(model.nodes, model.gens, bounds=capacity_max, doc='Generator cap')

#CONSTRAINTS
def prodcapa_rule(model, nodes, gens, time):
    return model.prod[nodes, gens, time] <= model.capa[nodes, gens]

model.prodCapa = Constraint(model.nodes, model.gens, model.time, rule=prodcapa_rule)

def getProductionCoeff(country, gens, time):
    if gens == 'Wind' or gens == 'PV':
        return

def produceDemand(model, nodes, gens, time):
    return 0

#OBJECTIVE FUNCTION
def objective_rule(model):
    return sum(#Add equation for the sum of all system costs.
    )

model.objective = Objective(rule=objective_rule, sense=minimize, doc='Objective function')


if __name__ == '__main__':

    opt = SolverFactory("gurobi_direct")
    opt.options["threads"] = 4
    print('Solving')
    results = opt.solve(model, tee=True)

    results.write()

    #Reading output - example
    capTot = {}
    for n in model.nodes:
        for g in model.gens:
            capTot[n, g] = model.capa[n, g].value/1e3 #GW


    costTot = value(model.objective) / 1e6 #Million EUR