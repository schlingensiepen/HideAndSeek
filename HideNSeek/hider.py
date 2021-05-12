from sympy import Circle

class Hider:
    vel = 5
    rotVel = 5

    playerSurface = None

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 90
        self.radius = 25

    def draw_circle(self, x = None, y = None):
        if x == None:
            x = self.x
        if y == None:
            y = self.y
        circle = Circle([x, y], self.radius)
        return circle

