import numpy as np

def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(line1, line2):
    A = line1[0]
    B = line1[1]
    C = line2[0]
    D = line2[1]
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


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

    


    def seeHider(self, hiders, obstacles):
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

            viewline = ((self.x, self.y), (hider.x, hider.y))

            #check if any obstacles block vision
            for obs in obstacles:
                obs_line = ((obs.x, obs.y + obs.height/2), (obs.x + obs.width, obs.y + obs.height/2))
                broken_los = intersect(viewline, obs_line)

                if broken_los == True:
                    los = False
                    break
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
