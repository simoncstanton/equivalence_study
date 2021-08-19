class Prisoners_dilemma:
    ''' Prisoners Dilemma gameform:
            Semantic View: CC, CD, DC, DD
            Interpretation: RR, ST, TS, PP
            (1)
                    COL:
                        C       D
            ROW:    C   3,3     0,5
                    D   5,0     1,1
            
            Ordinal representation:
                "g111": [(3,3),(1,4),(4,1),(2,2)],
            ---------------------------------------
            (2)
                            COL:
                            C/0     D/1
            ROW:    C/0     R       S
                    D/1     T       P
                    
                    [[R],[S]], [[T],[P]]
            (3)      
                            COL:
                            C/0     D/1
            ROW:    C/0     0,0     0,1
                    D/1     1,0     1,1
                    
                    [[R{0,0}],[S{0,1}]], [[T{1,0}],[P{1,1}]]
    '''
    def __init__(self, properties):
        self.properties = properties
        self.colloquial_name = "prisoners_dilemma"
        
        if self.properties["preferences"] == "ordinal":
            self.matrix = [[3,3],[1,4]], [[4,1],[2,2]]
        else:   # scalar
            self.matrix = [[3,3],[0,5]],[[5,0],[1,1]]
        #self.semantic_view = ('C', 'D')
        #self.mc = [(0,0)]
        
    def reward(self, actions):
        return self.matrix[actions[0]][actions[1]]
    
    def get_colloquial_name(self):
        return self.colloquial_name
        
    
    # def get_semantic_view(self, sv_index):
        # return self.semantic_view[sv_index]
