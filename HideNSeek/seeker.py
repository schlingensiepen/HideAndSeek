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
    seeAngle = 60

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 90
        self.radius = 25

    


    def see(self, hiders, obstacles):
        status = []

        for x, hider in enumerate(hiders):  
            entry = []   
            entry.append(hider)
            los = True
            viewline = ((self.x, self.y), (hider.x, hider.y))
            
            #check if any obstacles block vision
            for obs in obstacles:
                obs_line = ((obs.x, obs.y + obs.height/2), (obs.x + obs.width, obs.y + obs.height/2))
                broken_los = intersect(viewline, obs_line)

                if broken_los == True:
                    los = False
                    break

            if los == True:
                deltaX = hider.x - self.x
                if deltaX == 0:
                    deltaX = 0.0001
                deltaY = hider.y - self.y
                dis = int(np.sqrt(np.square(deltaX) + np.square(deltaY)))
                los_angle = int(np.rad2deg(np.arctan(deltaY / deltaX))) - 180
                los_angle = abs(los_angle)
                los_angle -= 90
                if hider.x > self.x:
                    los_angle += 180

                difAngle_seeker = abs(los_angle - self.angle)

                # sees and in range
                if dis < self.catchRadius and min(difAngle_seeker, 360 - difAngle_seeker) < self.seeAngle / 2:
                    entry.append('seeker_see')

                # sees but not in range
                elif min(difAngle_seeker, 360 - difAngle_seeker) < self.seeAngle / 2:
                    entry.append('seeker_seesemi')

                else:
                    entry.append('seeker_nosee')

                #same for hider
                hiderangle = hider.angle
                dif_Angle_hider = abs(los_angle + 180 - hiderangle)
                if min(dif_Angle_hider, 360 - dif_Angle_hider) < hider.seeAngle / 2:
                    entry.append('hider_see')
                else:
                    entry.append('hider_nosee')

                status.append(entry)
                   
            # no see
            else:
                status.append([hider, 'seeker_nosee', 'hider_nosee' ])
            return status
