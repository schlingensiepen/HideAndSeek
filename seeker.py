import numpy as np


class Seeker:
    vel = 5
    rotVel = 5
    playerSurface = None
    findRadius = 200
    findAngle = 70

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.angle = 90
        self.width = img.get_width()
        self.height = img.get_height()

    def seeHider(self, hiders):
        for x, hider in enumerate(hiders):

            deltaX = hider.getMiddleX() - self.getMiddleX()
            deltaY = hider.getMiddleY() - self.getMiddleY()

            dis = np.sqrt(np.square(deltaX) + np.square(deltaY))

            angle = np.rad2deg(np.tan(deltaY/deltaX))
            difAngle = abs(angle - self.angle)

            if dis < self.findRadius and min(difAngle, 360-difAngle) < np.divide(self.findAngle, 2):
                return x
            else:
                return -1

    def getMiddleX(self):
        x = self.x + self.width/2
        return x

    def getMiddleY(self):
        y = self.y + self.height / 2
        return y
