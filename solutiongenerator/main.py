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
POP_SIZE_MULTI = int(os.getenv('POPULATION_SIZE_MULTI', 1))
CHROMO_SIZE = int(os.getenv('SOLUTION_SIZE', 4))
CHROMO_SERIES_PROB = 0.9

app = fapi()
work_dir_ = os.getcwd()
data_dir_ = work_dir_ + "/" + "data"


@app.get("/")
async def root():
    dataGetter = GetProcessedData()
    td_cus_date, td_cus_tool, td_fac_date, td_fac_tool, td_cus_spp, td_fac_spp = dataGetter.getTasks()

    machineData_count = dataGetter.getMachines()

    popSize = machineData_count * POP_SIZE_MULTI
    popGenerator = GeneratePopulations(
        popSize, CHROMO_SIZE, CHROMO_SERIES_PROB)

    workersCount = psutil.cpu_count() * (psutil.cpu_count() //
                                         psutil.cpu_count(logical=False))

    popData = []

    tdcd_data_worker = None
    tdct_data_worker = None
    tdcspp_data_worker = None
    tdfd_data_worker = None
    tdft_data_worker = None
    tdfspp_data_worker = None

    with ThreadPoolExecutor(workersCount) as pool:
        if len(td_cus_date) != 0:
            tdcd_data_worker = pool.submit(
                popGenerator.constructPop, td_cus_date)
            popData = popData + tdcd_data_worker.result()
        if len(td_cus_tool) != 0:
            tdct_data_worker = pool.submit(
                popGenerator.constructPop, td_cus_tool)
            popData = popData + tdct_data_worker.result()
        if len(td_cus_spp) != 0:
            tdcspp_data_worker = pool.submit(
                popGenerator.constructPop, td_cus_spp)
            popData = popData + tdcspp_data_worker.result()
        if len(td_fac_date) != 0:
            tdfd_data_worker = pool.submit(
                popGenerator.constructPop, td_fac_date)
            popData = popData + tdfd_data_worker.result()
        if len(td_fac_tool) != 0:
            tdft_data_worker = pool.submit(
                popGenerator.constructPop, td_fac_tool)
            popData = popData + tdft_data_worker.result()
        if len(td_fac_spp) != 0:
            tdfspp_data_worker = pool.submit(
                popGenerator.constructPop, td_fac_spp)
            popData = popData + tdfspp_data_worker.result()

    # popData = tdcd_data_worker.result() + tdct_data_worker.result() + tdcspp_data_worker.result() + \
    #    tdfd_data_worker.result() + tdft_data_worker.result() + \
    #    tdfspp_data_worker.result()

    if not os.path.isdir(data_dir_):
        os.makedirs(data_dir_)

    data_file_path = data_dir_ + "/" + "population.json"
    data = {'data': popData}

    with open(data_file_path, 'w') as f:
        json.dump(data, f, indent=4)
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
