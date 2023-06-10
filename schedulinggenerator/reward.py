from datamodel import Task, Tool
import pandas as pd


class Reward():
    def rewardFnc(self, tasksData, toolsData, sysDate, machine, solution, givenSolutions):

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

            toolId = [k for k in toolsData['toolCode'] if toolsData['toolCode'][k] ==
                      selectedTask.toolCode and toolsData['toolSize'][k] == selectedTask.toolSize]

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
                    currentScore += 15
                else:
                    currentScore -= 15

            temptools.insert(j, temp)
            individualScore.pop(j)
            individualScore.insert(j, currentScore)

        if len(givenSolutions) != 0:
            if self.__list_exists(solution, givenSolutions):
                for s in individualScore:
                    s -= 15

        for genIndex in range(len(solution)):
            tempSol = solution.copy()
            temp = solution[genIndex]
            tempSol.pop(genIndex)
            for tempk in tempSol:
                if temp == tempk:
                    individualScore[genIndex] -= 15
                else:
                    individualScore[genIndex] += 5

            tempSol.insert(genIndex, temp)

        return individualScore

    def __list_exists(self, target_list, list_of_lists):
        for sublist in list_of_lists:
            if sublist == target_list:
                return True

        return False
