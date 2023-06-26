import requests as req
import pandas as pd


class GetProcessedData:
    def getTasks(self, url='http://127.0.0.1:3000/tasks',  # dpservice
                 timeout=10):
        req_task = req.get(url, timeout=timeout, headers={
                           'Content-Type': 'application/json'})
        taskdata = req_task.json()

        taskdata_df = pd.DataFrame(taskdata)
        taskdata_df['c_dueDate'] = pd.to_datetime(
            taskdata_df['c_dueDate']).astype('datetime64[ms]')

        '''
        Conditional Data 
        '''

        index_names_coustmer = taskdata_df[taskdata_df['c_dueDate'] == pd.to_datetime(
            '1970-01-01')].index

        index_names_factory = taskdata_df[taskdata_df['c_dueDate'] != pd.to_datetime(
            '1970-01-01')].index

        taskdata_df_coustmer = taskdata_df.copy()
        taskdata_df_coustmer.drop(index_names_coustmer, inplace=True)

        taskdata_df_factory = taskdata_df.copy()
        taskdata_df_factory.drop(index_names_factory, inplace=True)

        taskdata_df_coustmer_date = pd.DataFrame()
        taskdata_df_coustmer_tool = pd.DataFrame()
        taskdata_df_coustmer_spp = pd.DataFrame()
        taskdata_df_factory_date = pd.DataFrame()
        taskdata_df_factory_tool = pd.DataFrame()
        taskdata_df_factory_spp = pd.DataFrame()

        if len(taskdata_df_coustmer) != 0:
            taskdata_df_coustmer_date = self.__sortByDate(taskdata_df_coustmer)
            taskdata_df_coustmer_tool = self.__sortByToolCode(
                taskdata_df_coustmer)
            taskdata_df_coustmer_spp = self.__sortBySecondsPerProduct(
                taskdata_df_coustmer)

        if len(taskdata_df_factory) != 0:
            taskdata_df_factory_date = self.__sortByDate(taskdata_df_factory)
            taskdata_df_factory_tool = self.__sortByToolCode(
                taskdata_df_factory)
            taskdata_df_factory_spp = self.__sortBySecondsPerProduct(
                taskdata_df_factory)

        '''
        Sorting the Data by Due Date
        '''
        # taskdata_df_coustmer_date = self.__sortByDate(taskdata_df_coustmer)
        # taskdata_df_factory_date = self.__sortByDate(taskdata_df_factory)

        '''
        Sorting the Data by Tool Code and Tool Size
        '''
        # taskdata_df_coustmer_tool = self.__sortByToolCode(taskdata_df_coustmer)
        # taskdata_df_factory_tool = self.__sortByToolCode(taskdata_df_factory)

        '''
        Sorting the Data by Seconds Per Product
        '''
        # taskdata_df_coustmer_spp = self.__sortBySecondsPerProduct(
        #    taskdata_df_coustmer)
        # taskdata_df_factory_spp = self.__sortBySecondsPerProduct(
        #    taskdata_df_factory)

        return (taskdata_df_coustmer_date.index.astype(int),
                taskdata_df_coustmer_tool.index.astype(int),
                taskdata_df_factory_date.index.astype(int),
                taskdata_df_factory_tool.index.astype(int),
                taskdata_df_coustmer_spp.index.astype(int),
                taskdata_df_factory_spp.index.astype(int))

    def __sortByDate(self, taskData):
        sortData = taskData.sort_values(by=['c_dueDate'])
        return sortData

    def __sortByToolCode(self, taskData):
        sortData = taskData.sort_values(by=['toolCode', 'toolSize'])
        return sortData

    def __sortBySecondsPerProduct(self, taskData):
        sortData = taskData.sort_values(by=['secondsPerProduct'])
        return sortData

    def getMachines(self, url='http://127.0.0.1:3000/machines',  # dpservice
                    timeout=10):
        req_machine = req.get(url, timeout=timeout, headers={
                              'Content-Type': 'application/json'})
        machinedata = req_machine.json()

        machinedata_df = pd.DataFrame(machinedata)

        return machinedata_df.index.size
