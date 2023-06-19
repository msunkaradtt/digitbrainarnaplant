from getdata import GetData
from datamodel import Machine, Task
from reward import Reward
from gamodel.gamodel import GaModel

import copy
import pandas as pd
from fastapi import FastAPI as fapi
from fastapi.middleware.cors import CORSMiddleware
import os
import json

app = fapi()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

work_dir_ = os.getcwd()
data_dir_ = work_dir_ + "/" + "data"

status = {'finished': ""}


@app.get("/")
async def root():
    status['finished'] = ""

    maxit = int(os.getenv('GENERATIONS', 7))

    mu = float(os.getenv('MUTATION_RATE', 0.2))
    sigma = int(os.getenv('MUTATION_FLIP', 10))

    solAll = os.getenv('FLAG_ALL', "no")
    machineCount = int(os.getenv('MACHINE_COUNT', 10))

    systemDate = os.getenv('SYS_DATE', "2023-02-13T00:00:00.000")
    sysDate = pd.to_datetime(systemDate)

    getData = GetData()
    initPopData = getData.getinitPop()

    varifier = Reward()

    tasksData = getData.getTasks()
    machinesData = getData.getMachines()
    toolsData = getData.getTools()

    num_children = len(initPopData['data'])
    sol_size = len(initPopData['data'][0])

    gaModel = GaModel()

    taskKeys = [int(k) for k in tasksData['UID']]

    varmin = min(taskKeys)
    varmax = max(taskKeys)

    machineKeys = [mac for mac in machinesData['id'].keys()]
    getSolMachineKeys = []
    if solAll == "no":
        getSolMachineKeys = copy.deepcopy(machineKeys[:machineCount])
    elif solAll == "yes":
        getSolMachineKeys = copy.deepcopy(machineKeys)

    givenSolutions = []

    machineSolutions = {}

    machinePops = {}

    for macID in getSolMachineKeys:
        selectedMachine = Machine(id=machinesData['id'][macID],
                                  secondsPerProduct=machinesData['secondsPerProduct'][macID],
                                  name=machinesData['name'][macID],
                                  machines_name=machinesData['machines_name'][macID])

        machineScores = {}

        for solID in range(len(initPopData['data'])):
            score = varifier.rewardFnc(
                tasksData, toolsData, sysDate, selectedMachine, initPopData['data'][solID], givenSolutions)
            sumscore = sum(score)
            machineScores[solID] = {
                'solution': initPopData['data'][solID], 'cost': sumscore}

        matatedPop = {}

        for _ in range(maxit):
            costs = []

            learnpop = {}
            if (len(matatedPop) == 0):
                learnpop = copy.deepcopy(machineScores)
            else:
                learnpop = copy.deepcopy(matatedPop)

            for i in range(len(learnpop)):
                costs.append(learnpop[i]['cost'])

            learn(num_children, gaModel, learnpop, costs, mu, sigma,
                  varmin, varmax, varifier, tasksData, toolsData,
                  sysDate, selectedMachine, givenSolutions,
                  sol_size, matatedPop)

        bestsol = {}
        bestcost = 0

        for up in matatedPop:
            if matatedPop[up]['cost'] > bestcost:
                bestsol = matatedPop[up]
                bestcost = matatedPop[up]['cost']

        # print(f'Machine {macID}: Best Solution = {bestsol}')

        givenSolutions.append(bestsol['solution'])

        machineSolutions[macID] = bestsol
        machinePops[macID] = matatedPop

        matatedPop = {}

    if not os.path.isdir(data_dir_):
        os.makedirs(data_dir_)

    sol_data_file_path = data_dir_ + "/" + "machinesolutions.json"
    sol_data = {'data': machineSolutions}

    with open(sol_data_file_path, 'w') as f:
        json.dump(sol_data, f, indent=4)
        f.close()

    pop_data_file_path = data_dir_ + "/" + "machinepops.json"
    pop_data = {'data': machinePops}

    with open(pop_data_file_path, 'w') as f:
        json.dump(pop_data, f, indent=4)
        f.close()

    status['finished'] = "Done!"

    return {"message": "Updated the data!"}


@app.get("/getStatus")
async def get_status():
    return status


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


def learn(num_children, gaModel, learnpop, costs, mu,
          sigma, varmin, varmax, varifier, tasksData,
          toolsData, sysDate, selectedMachine, givenSolutions,
          sol_size, matatedPop):
    chId = 0

    while chId != num_children:
        c1 = {}
        c2 = {}

        p1 = gaModel.tournament_selection(learnpop, costs, 2)
        p2 = gaModel.tournament_selection(learnpop, costs, 2)

        c1, c2 = gaModel.crossover(p1, p2)

        c1 = gaModel.mutate(c1, mu, sigma)
        c2 = gaModel.mutate(c2, mu, sigma)

        gaModel.bounds(c1, varmin, varmax)
        gaModel.bounds(c2, varmin, varmax)

        c1['solution'] = c1['solution'].tolist()
        c2['solution'] = c2['solution'].tolist()

        c1['cost'] = sum(varifier.rewardFnc(tasksData, toolsData, sysDate,
                                            selectedMachine, c1['solution'], givenSolutions))

        c2['cost'] = sum(varifier.rewardFnc(tasksData, toolsData, sysDate,
                                            selectedMachine, c2['solution'], givenSolutions))

        if len(c1['solution']) == sol_size and len(c2['solution']) == sol_size:
            matatedPop[chId] = c1
            matatedPop[chId + 1] = c2
            chId += 2
