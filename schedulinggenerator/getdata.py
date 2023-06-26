import requests as req


class GetData:
    def getinitPop(self, url='http://127.0.0.1:3001/population',  # solservice
                   timeout=10):
        req_pop = req.get(url, timeout=timeout, headers={
                          'Content-Type': 'application/json'})
        popData = req_pop.json()

        return popData

    def getTasks(self, url='http://127.0.0.1:3000/tasks',  # dpservice
                 timeout=10):
        req_tasks = req.get(url, timeout=timeout, headers={
                            'Content-Type': 'application/json'})
        tasksData = req_tasks.json()

        return tasksData

    def getMachines(self, url='http://127.0.0.1:3000/machines',  # dpservice
                    timeout=10):
        req_machines = req.get(url, timeout=timeout, headers={
                               'Content-Type': 'application/json'})
        machinesData = req_machines.json()

        return machinesData

    def getTools(self, url='http://127.0.0.1:3000/tools', timeout=10):  # dpservice
        req_tools = req.get(url, timeout=timeout, headers={
                            'Content-Type': 'application/json'})
        toolsData = req_tools.json()

        return toolsData
