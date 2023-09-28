import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI as fapi
from fastapi import WebSocket
import pandas as pd
import copy
from getdata import GetData
from getmodel import GetModel
from datamodel import Machine, Task
from reward import Reward
import os
import asyncio
import time

modelURL = os.getenv(
    'MODEL_FILE_URL', "https://raw.githubusercontent.com/msunkaradtt/digitbrainarnaplant/dev2/schedulinggenerator/gamodel/gamodel.py")
getModel = GetModel()
getModel.getModel(modelURL)

try:
    from gamodel.gamodel import GaModel
except ImportError as e:
    print(e.msg)


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

completedMachines = 0

status = {'message': "", 'time': "", 'totalMac': "", 'completedMac': ""}

GENERATIONS = int(os.getenv('GENERATIONS', 6))  # 10
MUTATION_RATE = float(os.getenv('MUTATION_RATE', 0.2))
MUTATION_FLIP = float(os.getenv('MUTATION_FLIP', 0.55))
FLAG_ALL = os.getenv('FLAG_ALL', "no")
MACHINE_COUNT = int(os.getenv('MACHINE_COUNT', 3))
SYS_DATE = os.getenv('SYS_DATE', "2023-02-13T00:00")

# @app.get("/")
@app.websocket("/wslearn")
async def root(websocket: WebSocket):  # websocket: WebSocket
    global completedMachines, GENERATIONS, MUTATION_RATE, MUTATION_FLIP, FLAG_ALL, MACHINE_COUNT, SYS_DATE

    print(MACHINE_COUNT)
    print(type(MACHINE_COUNT))
    
    await websocket.accept()

    sysDate = pd.to_datetime(SYS_DATE)

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
    if FLAG_ALL == "no":
        getSolMachineKeys = copy.deepcopy(machineKeys[:MACHINE_COUNT])
    elif FLAG_ALL == "yes":
        getSolMachineKeys = copy.deepcopy(machineKeys)

    givenSolutions = []

    machineSolutions = {}

    machinePops = {}

    status['message'] = "Learning..."
    status['time'] = "0:0:0"
    status['totalMac'] = str(len(getSolMachineKeys))
    status['completedMac'] = "0"

    start_time = time.time()

    loop = asyncio.get_event_loop()

    worker_ = loop.run_in_executor(None, scheduling, getSolMachineKeys, machinesData, initPopData, varifier,
                                   tasksData, toolsData, sysDate, givenSolutions, GENERATIONS,
                                   num_children, gaModel, MUTATION_RATE, MUTATION_FLIP, varmin, varmax,
                                   sol_size, machineSolutions, machinePops)

    while True:
        if worker_.done():
            break

        end_time = time.time()
        time_lapsed = end_time - start_time
        con_time = timeConvert(time_lapsed)

        status['time'] = con_time
        status['completedMac'] = str(completedMachines)

        await websocket.send_json(status)
        await asyncio.sleep(0.1)

    completedMachines = 0
    status['message'] = "Done"
    await websocket.send_json(status)
    # return {"message": "Done"}

@app.get("/parameters")
async def get_parameters():
    global GENERATIONS, MUTATION_RATE, MUTATION_FLIP, FLAG_ALL, MACHINE_COUNT, SYS_DATE

    data_ = {
        'generations': str(GENERATIONS),
        'mutation_rate': str(MUTATION_RATE),
        'mutation_flip': str(MUTATION_FLIP),
        'sys_date': SYS_DATE,
        'flag_all': FLAG_ALL,
        'machine_count': str(MACHINE_COUNT)
    }

    return data_

@app.get("/updateparams")
async def set_parameters(gen, murate, muflip, sysdate, flagall, macount):
    global GENERATIONS, MUTATION_RATE, MUTATION_FLIP, FLAG_ALL, MACHINE_COUNT, SYS_DATE

    GENERATIONS = int(gen)
    MUTATION_RATE = float(murate)
    MUTATION_FLIP = float(muflip)
    SYS_DATE = sysdate
    FLAG_ALL = flagall
    MACHINE_COUNT = int(macount)

    return {"message": "Done"}

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


def scheduling(getSolMachineKeys, machinesData, initPopData, varifier,
               tasksData, toolsData, sysDate, givenSolutions,
               maxit, num_children, gaModel, mu, sigma, varmin, varmax,
               sol_size, machineSolutions, machinePops):

    global completedMachines
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

        con_max = 50
        con = 0
        while con != con_max:
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
            bestindex = 0

            for up in matatedPop:
                if matatedPop[up]['cost'] > bestcost:
                    bestsol = matatedPop[up]
                    bestcost = matatedPop[up]['cost']
                    bestindex = up

            # print(f'Machine {macID}: Best Solution = {bestsol}')

            if len(bestsol) != 0:
                valSol = validateSolution(selectedMachine, bestsol, tasksData)

                if valSol.count(1) >= len(bestsol['solution']) - 1:
                    zeroIndex = [zeo for zeo, e in enumerate(valSol) if e == 0]
                    taskIndex = [tas for tas in tasksData['secondsPerProduct'].keys(
                    ) if tasksData['secondsPerProduct'][tas] == selectedMachine.secondsPerProduct]
                    for ta in taskIndex:
                        ta_ = int(ta)
                        if ta_ not in bestsol['solution'] and len(zeroIndex) != 0:
                            bestsol['solution'].pop(zeroIndex[0])
                            bestsol['solution'].insert(zeroIndex[0], ta_)
                            machineScores[bestindex]['solution'] = bestsol['solution']
                            machineScores[bestindex]['cost'] = bestsol['cost'] + 5

                if 0 not in valSol:
                    givenSolutions.append(bestsol['solution'])

                    machineSolutions[macID] = bestsol
                    machinePops[macID] = matatedPop

                    # print(f'Machine {macID}: Best Solution = {bestsol}')

                    completedMachines += 1

                    matatedPop = {}

                    break

            con += 1

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


def timeConvert(sec):
    sec_ = sec % 60
    mins_ = sec // 60
    hours_ = mins_ // 60
    time_ = f"{round(hours_)}:{round(mins_)}:{round(sec_)}"
    return time_


def validateSolution(selectedMachine, bestSol, tasksData):

    trueConter = []
    for i in range(len(bestSol['solution'])):
        taskNo = str(bestSol['solution'][i])

        selectedTask = Task(UID=tasksData['UID'][taskNo],
                            secondsPerProduct=tasksData['secondsPerProduct'][taskNo],
                            toolCode=tasksData['toolCode'][taskNo],
                            toolSize=tasksData['toolSize'][taskNo],
                            dueDate=tasksData['dueDate'][taskNo],
                            qtyTotal=tasksData['qtyTotal'][taskNo],
                            c_dueDate=tasksData['c_dueDate'][taskNo])

        if selectedTask.secondsPerProduct == selectedMachine.secondsPerProduct:
            trueConter.append(1)
        else:
            trueConter.append(0)

    return trueConter
