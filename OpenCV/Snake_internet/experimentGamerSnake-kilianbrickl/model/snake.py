import pygame

class Snake:
    """A snake has a body that consists of several points.

    The body has a head (first point) and a tail (last point).
    """
    black = (0, 0, 0)
    headColor = (213, 50, 80)
    bodyColor = (255, 255, 255)
    damageColor = (255, 0, 0)

    def __init__(self, field,color, len = 1, x = 10, y = 10):
        """Start with a snake in a horizontal position."""
        self.field = field
        self.body = []
        self.growLength = 0
        for i in range(0, len):
            self.body.append((x - i, y))
        self.bodyColor = (255, 255, 255)
        self.headColor = (213, 50, 80)

    def move(self, dx, dy):
        """Move the snake in the given direction."""
        (x, y) = self.body[0] # get old position of head
        x += dx
        y += dy # calculate new position of head
        if self.growLength > 0:
            self.growLength -= 1 # grow
        else:
            self.body.pop() # remove tail
        self.body.insert(0, (x, y)) # insert new position of head
        if self.body[0] in self.body[1:]: # does the head collide with the rest of the body?
            return False # yes, then this is an invalid move
        elif x < 0 or x >= self.field.width or y < 0 or y >= self.field.height: # outside screen?
            return False
        else:
            return True # no

    def grow(self, length = 1):
        self.growLength = length

    def draw(self, damage = False):
        """Draw the body of the snake."""
        for i in range(0, len(self.body)):
            if damage:
                color = self.damageColor
            elif i == 0:
                color = self.headColor
            else:
                color = self.bodyColor

            (x, y) = self.body[i]
            size = self.field.blockSize
            rect = (x * size, y * size, size, size)
            pygame.draw.rect(self.field.screen, color, rect, 0)
            pygame.draw.rect(self.field.screen, self.black, rect, width=1)

