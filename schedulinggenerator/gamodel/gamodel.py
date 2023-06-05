import numpy as np
import copy

class GaModel():
    def __init__(self):
        pass

    def roulette_wheel_selection(self, p):

        c = np.cumsum(p)
        r = sum(p) * np.random.rand()
        ind = np.argwhere(r <= c)

        return ind[0][0]
    
    def crossover(self, p1, p2):
        c1 = copy.deepcopy(p1)
        c2 = copy.deepcopy(p2)

        cutpoint = len(c1['solution']) // 2
        c1['solution'] = p1['solution'][:cutpoint] + p2['solution'][cutpoint:]
        c2['solution'] = p2['solution'][:cutpoint] + p1['solution'][cutpoint:]

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

