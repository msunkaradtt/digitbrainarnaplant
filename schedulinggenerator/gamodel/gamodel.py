import numpy as np
import copy

class GaModel():
    def roulette_wheel_selection(self, p):

        c = np.cumsum(p)
        r = sum(p) * np.random.rand()
        ind = np.argwhere(r <= c)

        return ind[0][0]
    
    def crossover(self, p1, p2):
        c1 = copy.deepcopy(p1)
        c2 = copy.deepcopy(p2)
        
        cutpoint = len(c1['solution']) // 2

        c1['solution'] = [*p1['solution'][:cutpoint], *p2['solution'][cutpoint:]]
        c2['solution'] = [*p2['solution'][:cutpoint], *p1['solution'][cutpoint:]]

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
    
    def sort(self, arr):
        n = len(arr)

        for i in range(n-1):
            for j in range(0, n-i-1):
                if arr[j]['cost'] > arr[j+1]['cost']:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
            
            return arr

