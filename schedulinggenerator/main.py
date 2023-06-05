from getdata import GetData
from datamodel import Machine, Task, Tool
import numpy as np
from gamodel.gamodel import GaModel
import copy

getData = GetData()
initPopData = getData.getinitPop()

tasksData = getData.getTasks()
machinesData = getData.getMachines()
toolsData = getData.getTools()

gaModel = GaModel()

maxit = 501
beta = 1
prop_children = 1
npop = len(initPopData['data'])
num_children = int(np.round(prop_children * npop/2)*2)
mu = 0.2
sigma = 1 

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
            totalScore += 1
        else:
            totalScore -= 1
        
        if selectedTool.available > 0 and selectedTool.available != '':
            totalScore += 1
        else:
            totalScore -= 1

        totalScore += 0.5

        individualScore.append(totalScore)
    
    for j in range(len(tools)):
        currentScore = individualScore[j]
        temptools = tools.copy()
        temp = tools[j]
        temptools.pop(j)
        
        for k in temptools:
            if (temp.toolSize == k.toolSize and temp.toolCode == k.toolCode) and (k.toolSize != '' and k.toolCode != ''):
                currentScore += 0.5
            else:
                currentScore -= 0.5
        temptools.insert(j, temp)
        individualScore.pop(j)
        individualScore.insert(j, currentScore)

    return individualScore


selectedMachine = Machine(id=machinesData['id']['561'],
            secondsPerProduct=machinesData['secondsPerProduct']['561'],
            name=machinesData['name']['561'],
            machines_name=machinesData['machines_name']['561'])


bestsol_cost = np.inf
machineScores = {}

for i in range(len(initPopData['data'])):
    score = rewardFnc(selectedMachine, initPopData['data'][i])
    sumscore = sum(score)
    machineScores[i] = {'solution': initPopData['data'][i], 'cost': sumscore}

    if machineScores[i]['cost'] < bestsol_cost:
        pass
 
bestcost = np.empty(maxit)

#for it in range(maxit):
costs = []
for i in range(len(machineScores)):
    costs.append(machineScores[i]['cost'])
costs = np.array(costs)
avg_cost = np.mean(costs)
if avg_cost != 0:
    costs = costs/avg_cost
probs = np.exp(-beta*costs)

for _ in range(2//2):
    p1 = machineScores[gaModel.roulette_wheel_selection(probs)]
    p2 = machineScores[gaModel.roulette_wheel_selection(probs)]

    print("Selection")
    print(p1)
    print(p2)
    print("============")

    c1, c2 = gaModel.crossover(p1, p2)

    print("Crossover")
    print(c1)
    print(c2)
    print("============")

    c1 = gaModel.mutate(c1, mu, sigma)
    c2 = gaModel.mutate(c2, mu, sigma)
    print("Mutation")
    print(c1)
    print(c2)
    print("============")

    gaModel.bounds(c1, varmin, varmax)
    gaModel.bounds(c2, varmin, varmax)

    c1['cost'] = sum(rewardFnc(selectedMachine, c1['solution']))
    
    if type(bestsol_cost) == float:
        if c1['cost'] < bestsol_cost:
            bestsol_cost = copy.deepcopy(c1)
    else:
        if c1['cost'] < bestsol_cost['cost']:
            bestsol_cost = copy.deepcopy(c1)