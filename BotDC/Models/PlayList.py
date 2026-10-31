from collections import deque


class PlayList:
    def __init__(self) -> None:
        self.playque = deque()
        self.indexMusic = 0

    def next(self):
        if len(self.playque) >= (self.indexMusic + 2):
            self.indexMusic += 1
            return self.playque[self.indexMusic]
        return False

    def back(self):
        if (self.indexMusic - 1) < 0 or not self.playque:
            return False
        self.indexMusic -= 1
        return self.playque[self.indexMusic]

    def clean(self):
        self.playque = deque()
        self.indexMusic = 0

    def add(self, track):
        self.playque.append(track)

    def atual(self):
        if not self.playque or self.indexMusic >= len(self.playque):
            return None
        return self.playque[self.indexMusic]

    def returnList(self):
        return list(self.playque)

    def returnIndexMusic(self):
        return self.indexMusic
