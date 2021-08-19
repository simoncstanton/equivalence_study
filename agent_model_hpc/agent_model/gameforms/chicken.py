class Chicken:
    ''' Chicken gameform:
            Semantic View: CC, CD, DC, DD
            Interpretation: R, ST, TS, P
                    COL:
                        C       D
            ROW:    C   4,4     2,5
                    D   5,2     0,0
            
            Ordinal representation:
                "g122": [[3,3],[2,4]], [[4,2],[1,1]],
            ---------------------------------------
                            COL:
                            C/0     D/1
            ROW:    C/0     R       S
                    D/1     T       P
                    
                    [[R],[S]], [[T],[P]]
                    
                            COL:
                            C/0     D/1
            ROW:    C/0     0,0     0,1
                    D/1     1,0     1,1

                    [[R{0,0}],[S{0,1}]], [[T{1,0}],[P{1,1}]]
                
    '''
    def __init__(self, properties):
        self.properties = properties
        
        if self.properties["preferences"] == "ordinal":
            self.matrix = [[3,3],[2,4]], [[4,2],[1,1]]
        else:
            self.matrix = [[4,4],[2,5]],[[5,2],[0,0]]
        self.semantic_view = ('C', 'D')
        self.mc = [(0,0)]
        
    def reward(self, actions):
        return self.matrix[actions[0]][actions[1]]
    
    def get_semantic_view(self, sv_index):
        return self.semantic_view[sv_index]
