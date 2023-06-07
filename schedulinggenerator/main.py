from getdata import GetData
from datamodel import Machine, Task
from reward import Reward
import numpy as np
from gamodel.gamodel import GaModel
import copy
import pandas as pd

from fastapi import FastAPI as fapi

import os
import json

app = fapi()
work_dir_ = os.getcwd()
data_dir_ = work_dir_ + "/" + "data"

maxit = 10
beta = 1
num_children = 4
mu = 0.7
sigma = -2 
systemDate = "2023-02-13T00:00:00.000"
sysDate = pd.to_datetime(systemDate)

@app.get("/")
async def root():
    getData = GetData()
    initPopData = getData.getinitPop()

    varifier = Reward()

    tasksData = getData.getTasks()
    machinesData = getData.getMachines()
    toolsData = getData.getTools()

    gaModel = GaModel()

    taskKeys = [int(k) for k in tasksData['UID']]
    varmin = min(taskKeys)
    varmax = max(taskKeys)

    givenSolutions = []

    machineSolutions = {}
    machinePops = {}

    for macID in machinesData['id'].keys():
        selectedMachine = Machine(id=machinesData['id'][macID],
                                  secondsPerProduct=machinesData['secondsPerProduct'][macID],
                                  name=machinesData['name'][macID],
                                  machines_name=machinesData['machines_name'][macID])
    
        machineScores = {}
    
        for i in range(len(initPopData['data'])):
            score = varifier.rewardFnc(tasksData, toolsData, sysDate, selectedMachine, initPopData['data'][i], givenSolutions)
            sumscore = sum(score)
            machineScores[i] = {'solution': initPopData['data'][i], 'cost': sumscore}
    
        bestsol = {}
        bestsol_cost = 0
    
        #for ii in range(len(initPopData['data'])):
        #    if machineScores[ii]['cost'] > bestsol_cost:
        #        bestsol = copy.deepcopy(machineScores[ii])
        #        bestsol_cost = machineScores[ii]['cost']
    
        bestcost = np.empty(maxit)

        for it in range(maxit):
            costs = []
    
            for i in range(len(machineScores)):
                costs.append(machineScores[i]['cost'])
    
            costs = np.array(costs)
    
            avg_cost = np.mean(costs)
    
            if avg_cost != 0:
                costs = costs/avg_cost
    
            probs = np.exp(np.float128(-beta*costs))
    
            for _ in range(num_children//2):
                p1 = machineScores[gaModel.roulette_wheel_selection(probs)]
                p2 = machineScores[gaModel.roulette_wheel_selection(probs)]
            
                c1, c2 = gaModel.crossover(p1, p2)
            
                c1 = gaModel.mutate(c1, mu, sigma)
                c2 = gaModel.mutate(c2, mu, sigma)
        
                gaModel.bounds(c1, varmin, varmax)
                gaModel.bounds(c2, varmin, varmax)
        
                c1['cost'] = sum(varifier.rewardFnc(tasksData, toolsData, sysDate, selectedMachine, c1['solution'].tolist(), givenSolutions))
                c2['cost'] = sum(varifier.rewardFnc(tasksData, toolsData, sysDate, selectedMachine, c2['solution'].tolist(), givenSolutions))

                c1['solution'] = c1['solution'].tolist()
                c2['solution'] = c2['solution'].tolist()

                if c1['cost'] > bestsol_cost:
                    bestsol = copy.deepcopy(c1)
                    bestsol_cost = c1['cost']
        
                if c2['cost'] > bestsol_cost:
                    bestsol = copy.deepcopy(c2)
                    bestsol_cost = c2['cost']
 
            machineScores[len(machineScores)] = c1
            machineScores[len(machineScores)] = c2
        
            machineScores = gaModel.sort(machineScores)

            bestcost[it] = bestsol_cost

            #print(f'Iteration {it}: Best Cost = {bestcost[it]}, Best Cost = {bestsol}')
    
        givenSolutions.append(bestsol['solution'])

        machineSolutions[macID] = bestsol
        machinePops[macID] = machineScores

    if not os.path.isdir(data_dir_):
        os.makedirs(data_dir_)

    sol_data_file_path = data_dir_ + "/" + "machinesolutions.json"
    sol_data = {'data': machineSolutions}

    with open(sol_data_file_path, 'w') as f:
        json.dump(sol_data, f, indent=2)
        f.close()
    
    pop_data_file_path = data_dir_ + "/" + "machinepops.json"
    pop_data = {'data': machinePops}
    
    with open(pop_data_file_path, 'w') as f:
        json.dump(pop_data, f, indent=2)
        f.close()
        
    return {"message": "Updated the data!"}

@app.get("/machinetasks")
async def get_machinetasks():
    getData = GetData()

    tasksData = getData.getTasks()
    machinesData = getData.getMachines()

    file_path = data_dir_ + "/" + "machinesolutions.json"
    data = {}
    with open(file_path) as f:
        data = json.load(f)
        f.close()
    
    consData = {}
    for macID in data['data'].keys():
        selectedMachine = Machine(id=machinesData['id'][macID],
                                  secondsPerProduct=machinesData['secondsPerProduct'][macID],
                                  name=machinesData['name'][macID],
                                  machines_name=machinesData['machines_name'][macID])

        taskList = {}
        for taskNo in data['data'][macID]['solution']:
            taskno = str(taskNo)
            selectedTask = Task(UID=tasksData['UID'][taskno],
                                secondsPerProduct=tasksData['secondsPerProduct'][taskno],
                                toolCode=tasksData['toolCode'][taskno],
                                toolSize=tasksData['toolSize'][taskno],
                                dueDate=tasksData['dueDate'][taskno],
                                qtyTotal=tasksData['qtyTotal'][taskno],
                                c_dueDate=tasksData['c_dueDate'][taskno])
            
            taskList[taskno] = selectedTask
        
        consData[macID] = {'machine': selectedMachine, 'tasks': taskList}
    
    return consData
