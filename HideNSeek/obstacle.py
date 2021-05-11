from sympy import Polygon

class Obstacle:
    playerSurface = None
    width = 100
    height = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        #self.width = width
        #self.height = height
        
        self.locked = False


    def sympy_obstacle(self, obstacle):
            obst = Polygon([self.x, self.y], [self.x + self.width, self.y], [self.x + self.width, self.y + self.height], [self.x, self.y + self.height])
            return obst

