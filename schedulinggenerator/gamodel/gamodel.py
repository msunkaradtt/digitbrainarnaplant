import numpy as np
import copy
import random


class GaModel():
    def tournament_selection(self, machineScores, costs, tournament_size):
        tournament = random.sample(
            range(len(machineScores)), tournament_size)
        winner = None
        max_cost = float('-inf')
        for index in tournament:
            if costs[index] > max_cost:
                max_cost = costs[index]
                winner = machineScores[index]

        return winner

    def crossover(self, p1, p2):
        c1 = copy.deepcopy(p1)
        c2 = copy.deepcopy(p2)

        cutpoint = len(c1['solution']) // 2

        c1['solution'] = [*p1['solution']
                          [:cutpoint], *p2['solution'][cutpoint:]]
        c2['solution'] = [*p2['solution']
                          [:cutpoint], *p1['solution'][cutpoint:]]

        return c1, c2

    def mutate(self, c, mu, sigma):
        y = copy.deepcopy(c)

        flag = np.random.rand(*(np.array(c['solution']).shape)) <= mu

        ind = np.argwhere(flag)

        if len(ind) != 0:
            for i in ind:
                y['solution'][i[0]] += sigma

        return y

    def bounds(self, c, varmin, varmax):
        c['solution'] = np.maximum(c['solution'], varmin)
        c['solution'] = np.minimum(c['solution'], varmax)
