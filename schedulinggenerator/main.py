from getdata import GetData
from datamodel import Machine, Task, Tool
import numpy as np
from gamodel.gamodel import GaModel
import copy
import pandas as pd

getData = GetData()
initPopData = getData.getinitPop()

tasksData = getData.getTasks()
machinesData = getData.getMachines()
toolsData = getData.getTools()

gaModel = GaModel()

maxit = 20
beta = 1
num_children = 8
mu = 0.2
sigma = 1 

systemDate = "2023-02-13T00:00:00.000"
sysDate = pd.to_datetime(systemDate)

taskKeys = [int(k) for k in tasksData['UID']]
varmin = min(taskKeys)
varmax = max(taskKeys)

def rewardFnc(machine, solution):

    individualScore = []

    tools = []
    for i in range(len(solution)):
        taskNo = str(solution[i])
        
        selectedTask = Task(UID=tasksData['UID'][taskNo],
                            secondsPerProduct=tasksData['secondsPerProduct'][taskNo],
                            toolCode=tasksData['toolCode'][taskNo],
                            toolSize=tasksData['toolSize'][taskNo],
                            dueDate=tasksData['dueDate'][taskNo],
                            qtyTotal=tasksData['qtyTotal'][taskNo],
                            c_dueDate=tasksData['c_dueDate'][taskNo])
        
        toolId = [k for k in toolsData['toolCode'] if toolsData['toolCode'][k] == selectedTask.toolCode and toolsData['toolSize'][k] == selectedTask.toolSize]
        
        if len(toolId) != 0:
            selectedTool = Tool(toolSize=toolsData['toolSize'][toolId[0]], 
                                toolCode=toolsData['toolCode'][toolId[0]],
                                total=toolsData['total'][toolId[0]],
                                available=toolsData['available'][toolId[0]])
        else:
            selectedTool = Tool(toolSize="", 
                                toolCode="",
                                total=0,
                                available=0)
        
        tools.append(selectedTool)
        
        totalScore = 0
        
        if machine.secondsPerProduct == selectedTask.secondsPerProduct:
            totalScore += 10
        else:
            totalScore -= 10
        
        if selectedTool.available > 0 and selectedTool.available != '':
            totalScore += 10
        else:
            totalScore -= 10

        totalScore += 5

        date = pd.to_datetime(selectedTask.c_dueDate)
        days = (date.date() - sysDate.date()).days

        if days < 0:
            totalScore -= 15
        elif days > 0 and days < 3:
            totalScore += 15
        elif days > 3 and days <= 5:
            totalScore += 10
        else:
            totalScore += 5

        individualScore.append(totalScore)
    
    for j in range(len(tools)):
        currentScore = individualScore[j]
        temptools = tools.copy()
        temp = tools[j]
        temptools.pop(j)
        
        for k in temptools:
            if (temp.toolSize == k.toolSize and temp.toolCode == k.toolCode) and (k.toolSize != '' and k.toolCode != ''):
                currentScore += 5
            else:
                currentScore -= 5
        temptools.insert(j, temp)
        individualScore.pop(j)
        individualScore.insert(j, currentScore)

    return individualScore


selectedMachine = Machine(id=machinesData['id']['561'],
            secondsPerProduct=machinesData['secondsPerProduct']['561'],
            name=machinesData['name']['561'],
            machines_name=machinesData['machines_name']['561'])


machineScores = {}

for i in range(len(initPopData['data'])):
    score = rewardFnc(selectedMachine, initPopData['data'][i])
    sumscore = sum(score)
    machineScores[i] = {'solution': initPopData['data'][i], 'cost': sumscore}

bestsol = {}
bestsol_cost = 0

for ii in range(len(initPopData['data'])):

    if machineScores[ii]['cost'] > bestsol_cost:
        bestsol = copy.deepcopy(machineScores[ii])
        bestsol_cost = machineScores[ii]['cost']


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
        
        c1['cost'] = sum(rewardFnc(selectedMachine, c1['solution']))
        c2['cost'] = sum(rewardFnc(selectedMachine, c2['solution']))

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

    print(f'Iteration {it}: Best Cost = {bestcost[it]}, Best Cost = {bestsol}')
