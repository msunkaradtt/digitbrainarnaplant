import numpy as np


class GeneratePopulations:
    def __init__(self, popSize, chromoSize, proSeries):
        self.__popSize_ = popSize
        self.__chromoSize_ = chromoSize
        self.__proSeries_ = proSeries

    def constructPop(self, data):
        popList = []

        currentIndex = 0
        for _ in range(self.__popSize_):
            chromo = []
            if np.random.rand(1) < self.__proSeries_ and currentIndex < len(data) - 1:
                chromo = data[currentIndex: currentIndex + self.__chromoSize_]
                popList.append(chromo.tolist())
                currentIndex += self.__chromoSize_
            else:
                for __ in range(self.__chromoSize_):
                    while (True):
                        taskID = np.random.randint(min(data), max(data) + 1)
                        if taskID in data:
                            break

                    chromo.append(taskID)

                popList.append(chromo)

        return popList
