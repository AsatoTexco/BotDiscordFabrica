from collections import deque

class PlayList:

    def __init__(self) -> None:
        self.playque = deque()
        self.indexMusic = 0

    def next(self):
        if(len(self.playque) >= (self.indexMusic +  2)):
            self.indexMusic += 1 
            return  self.playque[self.indexMusic]  
        else:
            return False
        
    def back(self): 
        if((self.indexMusic - 1) < 0):
            return False
        else:
            self.indexMusic -= 1 
            return self.playque[self.indexMusic] 
    
    def clean(self):    
        self.playque = deque() 

    def add(self,track): 
        self.playque.append(track) 

    def atual(self):
        return self.playque[self.indexMusic]
    
    def returnList(self):
        return self.playque
    
    def returnIndexMusic(self):
        return self.indexMusic