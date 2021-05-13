import numpy as np
from sympy import Circle, Segment


class Seeker:
    vel = 3
    rotVel = 5
    playerSurface = None
    catchRadius = 200
    findAngle = 60

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 90
        self.radius = 25

    def draw_circle(self, x=None, y=None):
        if x == None:
            x = self.x
        if y == None:
            y = self.y
        circle = Circle([x, y], self.radius)
        return circle

    def seeHider(self, hiders, obstacles):
        seeker_circle = self.draw_circle()
        status = []

        for x, hider in enumerate(hiders):
            hider_circle = hider.draw_circle()
            deltaX = hider.x - self.x
            if deltaX == 0:
                deltaX = 0.0001
            deltaY = hider.y - self.y
            los = True
            dis = int(np.sqrt(np.square(deltaX) + np.square(deltaY)))
            angle = int(np.rad2deg(np.arctan(deltaY / deltaX))) - 180
            angle = abs(angle)
            angle -= 90
            if hider.x > self.x:
                angle += 180
            difAngle = abs(angle - self.angle)

            #viewline_center = Segment([self.x, self.y], [hider.x, hider.y])
            # tangente1, tangente2 = hider_circle.tangent_lines([self.x, self.y])
            # seg = Segment(tangente1[0], tangente1[1])
            # print(tangente1, tangente2)

            '''for obs in obstacles:
                broken_los = viewline_center.intersection(obs)
                if broken_los:
                    los = False
                    break'''
            # sees and in range
            if dis < self.catchRadius and min(difAngle, 360 - difAngle) < self.findAngle / 2 and los == True:
                status.append([x, 0])
            # sees but not in range
            elif min(difAngle, 360 - difAngle) < self.findAngle / 2 and los == True:
                status.append([x, 1])
            # no see
            else:
                status.append([x, 2])
            return status
