import time

class FpsCounter:
    def __init__(self):
        self.p_time = 0
        self.c_time = 0

    def update(self):
        self.c_time = time.time()
        fps = 1 / (self.c_time - self.p_time) if (self.c_time - self.p_time) > 0 else 0
        self.p_time = self.c_time
        return int(fps)