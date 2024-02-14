from collections import deque

class PlayList:

    def __init__(self) -> None:
        self.playque = deque()

    def add(self,track): 
        self.playque.append(track)

    def next(self):
        if(len(self.playque) > 0):
            response = self.playque[0]
            self.playque.popleft()
            return response
        else:
            return False
        
