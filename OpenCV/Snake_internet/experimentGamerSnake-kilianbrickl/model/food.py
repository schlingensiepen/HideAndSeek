import pygame
import random

class Food():
    def __init__(self, field):
        self.field = field
        self.x = random.randint(0, field.width - 1)
        self.y = random.randint(0, field.height - 1)
        self.color = (0, 255, 0)

    def draw(self):
        size = self.field.blockSize
        rect = (self.x * size, self.y * size, size, size)
        pygame.draw.rect(self.field.screen, self.color, rect, 0)
