import math

class LandUse:
    "This class is to define landuse"
    
    def __init__(self,name,value):
        self.name = name
        self.value = value
        self.image = None
        self.num_of_rings = None
        self.efs = []
    
    def append_efs(self,ef):
        self.efs.append(ef)
    
    def get_rings(self):
        rings = {}
        for c in range(0-self.num_of_rings,self.num_of_rings+1):
            for v in range(0-self.num_of_rings,self.num_of_rings+1):
                D = round(math.sqrt(c**2 + v**2)) 
                for i in range(1,self.num_of_rings+1):
                    if D == i:
                        if i in rings.keys():
                            rings[i].append([c,v])
                        else:
                            rings[i] = [[c,v]]
        return rings
    
    def validate_extent(self,i,j):
        if i>=0 and i<self.image.shape[0] and j>=0 and j<self.image.shape[1]:
            return True
        else:
            return False
