from collections import Counter

class Trial:

    def __init__(self, agents, matrix):
        self.agents = agents
        self.matrix = matrix
        self.distribution = Counter({(0,0): 0, (0,1): 0, (1,0): 0, (1,1): 0})
    
    def step(self, t, previous_step):
        actions = []
        
        # to consider, randomise order of agent's steps:
        #   does not modify list. log and check equal share of first step  [TODO]
        #       for a in sorted(self.agents,key=lambda _: random.random()):
        
        for a in self.agents:
            actions.append(a.step(t, previous_step))
        
        (p0, p1) = self.matrix[actions[0]][actions[1]]
        
        self.agents[0].previous_reward = p0
        self.agents[1].previous_reward = p1
        self.agents[0].opponent_previous_reward = p1
        self.agents[1].opponent_previous_reward = p0
        self.distribution[tuple(actions)] += 1
        
        return actions


    def final_step(self, t, previous_step):
        for a in self.agents:
            a.final_step(t, previous_step)
        
    # tuple here so can hash into Counter self.distribution   
    def get_CC(self):
        return self.distribution[(0, 0)]
        
    def get_CD(self):
        return self.distribution[(0, 1)]
    
    def get_DC(self):
        return self.distribution[(1, 0)] 
    
    def get_DD(self):
        return self.distribution[(1, 1)]        