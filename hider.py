class Hider:
    vel = 5
    rotVel = 5

    playerSurface = None

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.angle = 90
        self.width = img.get_width()
        self.height = img.get_height()

    def getMiddleX(self):
        x = self.x + self.width / 2
        return x

    def getMiddleY(self):
        y = self.y + self.height / 2
        return y