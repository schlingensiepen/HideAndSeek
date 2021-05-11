import pygame

class Field():
    fieldColor = (0, 0, 0)

    def __init__(self, screen, width, height, blockSize,color = 12800):
        self.screen = screen
        self.width = width
        self.height = height
        self.blockSize = blockSize
        self.fieldColor = (0, 0, 0)
        #print self.fieldColor

    def draw(self):
        self.screen.fill(self.fieldColor)
