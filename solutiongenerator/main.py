from getprocesseddata import GetProcessedData
from generatepopulations import GeneratePopulations

import os
import json

from fastapi import FastAPI as fapi
from concurrent.futures import ThreadPoolExecutor
import psutil

'''
Global Config Parameters
'''
POP_SIZE_MULTI = 4
CHROMO_SIZE = 4
CHROMO_SERIES_PROB = 0.8

app = fapi()
work_dir_ = os.getcwd()
data_dir_ = work_dir_ + "/" + "data"

@app.get("/")
async def root():
    dataGetter = GetProcessedData()
    td_cus_date, td_cus_tool, td_fac_date, td_fac_tool = dataGetter.getTasks()
    machineData_count = dataGetter.getMachines()
    
    popSize = machineData_count * POP_SIZE_MULTI
    popGenerator = GeneratePopulations(popSize, CHROMO_SIZE, CHROMO_SERIES_PROB);

    workersCount = psutil.cpu_count() * (psutil.cpu_count() // psutil.cpu_count(logical=False))

    with ThreadPoolExecutor(workersCount) as pool:
        tdcd_data_worker = pool.submit(popGenerator.constructPop, td_cus_date)
        tdct_data_worker = pool.submit(popGenerator.constructPop, td_cus_tool)
        tdfd_data_worker = pool.submit(popGenerator.constructPop, td_fac_date)
        tdft_data_worker = pool.submit(popGenerator.constructPop, td_fac_tool)

    
    popData = tdcd_data_worker.result() + tdct_data_worker.result() + tdfd_data_worker.result() + tdft_data_worker.result()
    
    if not os.path.isdir(data_dir_):
        os.makedirs(data_dir_)

    data_file_path = data_dir_ + "/" + "population.json"
    data = {'data': popData}

    with open(data_file_path, 'w') as f:
        json.dump(data, f, indent=2)
        f.close()
    
    return {"message": "Updated the data!"}

@app.get("/population")
async def get_tasks():
    file_path = data_dir_ + "/" + "population.json"
    data = {}
    with open(file_path) as f:
        data = json.load(f)
        f.close()

    return data
