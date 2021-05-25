from sympy import Circle

class Hider:
    vel = 6
    rotVel = 5
    seeAngle = 60

    playerSurface = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 270
        self.radius = 25

    def draw_circle(self, x = None, y = None):
        if x == None:
            x = self.x
        if y == None:
            y = self.y
        circle = Circle([x, y], self.radius)
        return circle

