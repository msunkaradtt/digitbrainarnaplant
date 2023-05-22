import requests as req
import pandas as pd

class GetProcessedData:
    def getTasks(self, url = 'http://127.0.0.1:8000/tasks', 
                 timeout = 10):
        req_task = req.get(url, timeout = timeout, headers = {'Content-Type': 'application/json'})
        taskdata = req_task.json()
        
        taskdata_df = pd.DataFrame(taskdata)
        taskdata_df['c_dueDate'] = pd.to_datetime(taskdata_df['c_dueDate']).astype('datetime64[ms]')

        '''
        Conditional Data 
        '''

        index_names_coustmer = taskdata_df[taskdata_df['c_dueDate'] == pd.to_datetime('1970-01-01')].index
        index_names_factory = taskdata_df[taskdata_df['c_dueDate'] != pd.to_datetime('1970-01-01')].index

        taskdata_df_coustmer = taskdata_df.copy()
        taskdata_df_coustmer.drop(index_names_coustmer, inplace=True)

        taskdata_df_factory = taskdata_df.copy()
        taskdata_df_factory.drop(index_names_factory, inplace=True)

        '''
        Sorting the Data by Due Date
        '''
        taskdata_df_coustmer_date = self.__sortByDate(taskdata_df_coustmer)
        taskdata_df_factory_date = self.__sortByDate(taskdata_df_factory)

        '''
        Sorting the Data by Tool Code and Tool Size
        '''
        taskdata_df_coustmer_tool = self.__sortByToolCode(taskdata_df_coustmer)
        taskdata_df_factory_tool = self.__sortByToolCode(taskdata_df_factory)

        return taskdata_df_coustmer_date.index.astype(int), taskdata_df_coustmer_tool.index.astype(int), taskdata_df_factory_date.index.astype(int), taskdata_df_factory_tool.index.astype(int)
    
    def __sortByDate(self, taskData):
        sortData = taskData.sort_values(by=['c_dueDate'])
        return sortData
        

    def __sortByToolCode(self, taskData):
        sortData = taskData.sort_values(by=['toolCode', 'toolSize'])
        return sortData

    
    def getMachines(self, url = 'http://127.0.0.1:8000/machines', 
                    timeout = 10):
        req_machine = req.get(url, timeout = timeout, headers = {'Content-Type': 'application/json'})
        machinedata = req_machine.json()
        
        machinedata_df = pd.DataFrame(machinedata)
        
        return machinedata_df.index.size


