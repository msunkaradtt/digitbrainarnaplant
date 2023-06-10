from datareader import DataReader
from datapreprocessor import DataPreProcessor
import os
from fastapi import FastAPI as fapi
import json
import pandas as pd
from datetime import datetime, timedelta

app = fapi()
work_dir_ = os.getcwd()
data_dir_ = work_dir_ + "/" + "data"

ENV_TASKS_URL = os.getenv(
    'ENV_TASKS_URL', 'https://meteo-de-oscar.proxy.beeceptor.com/digitbrain/tasks')
ENV_TOOLS_URL = os.getenv(
    'ENV_TOOLS_URL', 'https://meteo-de-oscar.proxy.beeceptor.com/digitbrain/tools')
ENV_MACHINES_URL = os.getenv(
    'ENV_MACHINES_URL', 'https://meteo-de-oscar.proxy.beeceptor.com/digitbrain/machines')


def __converdate(x):
    timeStamp_ = x.split("(")[1].split(")")[0]

    date_ = datetime(1970, 1, 1, 0, 0, 0)

    if len(timeStamp_) == 13:
        date_ = datetime.fromtimestamp(
            int(timeStamp_) / 1000).strftime("%d/%m/%Y")
    else:
        date_ = (datetime(1970, 1, 1) +
                 timedelta(milliseconds=int(timeStamp_) % 1000)).strftime("%d/%m/%Y")

    return date_


@app.get("/")
async def root():
    endpoints = [ENV_TASKS_URL, ENV_TOOLS_URL, ENV_MACHINES_URL]
    x = DataReader(endpoints)
    await x.fetch_main()

    taskList = ['UID', 'secondsPerProduct',
                'toolCode', 'toolSize', 'dueDate', 'qtyTotal']
    toolList = ['id', 'toolSize', 'toolCode', 'total', 'available']
    machineList = ['id', 'secondsPerProduct',
                   'name', 'machines_id', 'machines_name']

    p1 = DataPreProcessor(x.tasksData_, False, None, None)
    p1_data = p1.pp_selectData(taskList)
    p1_data['c_dueDate'] = p1_data['dueDate'].apply(__converdate)
    p1_data['c_dueDate'] = pd.to_datetime(p1_data['c_dueDate'], dayfirst=True)

    p2 = DataPreProcessor(x.toolsData_, False, None, None)
    p2_data = p2.pp_selectDataIndexed(toolList, 'id')

    machinemetaList = ['id', 'name', 'secondsPerProduct']
    p3 = DataPreProcessor(x.machinesData_, True, 'machines', machinemetaList)
    p3_data = p3.pp_selectDataTransformed(machineList, 'machines_id')

    if not os.path.isdir(data_dir_):
        os.makedirs(data_dir_)

    file_path_1 = data_dir_ + "/" + "tasks.json"
    p1_data.to_json(file_path_1, indent=4, date_format='iso', date_unit='ms')
    file_path_2 = data_dir_ + "/" + "tools.json"
    p2_data.to_json(file_path_2, indent=4)
    file_path_3 = data_dir_ + "/" + "machines.json"
    p3_data.to_json(file_path_3, indent=4)

    return {"message": "Updated the data!"}


@app.get("/tasks")
async def get_tasks():
    file_path = data_dir_ + "/" + "tasks.json"
    data = {}
    with open(file_path) as f:
        data = json.load(f)
        f.close()

    return data


@app.get("/tools")
async def get_tools():
    file_path = data_dir_ + "/" + "tools.json"
    data = {}
    with open(file_path) as f:
        data = json.load(f)
        f.close()

    return data


@app.get("/machines")
async def get_machines():
    file_path = data_dir_ + "/" + "machines.json"
    data = {}
    with open(file_path) as f:
        data = json.load(f)
        f.close()

    return data
