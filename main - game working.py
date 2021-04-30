from itertools import cycle
import random
import sys
import numpy as np
import os
import neat
import pygame
from pygame.locals import *
from hider import Hider
from seeker import Seeker
from object import Object
from sympy import *
from sympy.geometry import *

FPS = 30
SCREENWIDTH = 800
SCREENHEIGHT = 800
SCALING = 1

IMAGES = {}
HITMASKS = {}


def main():
    score = loopIter = 0

    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
    pygame.display.set_caption('Hide and Seek')

    IMAGES['background'] = pygame.image.load('sprites/bg.png').convert_alpha()
    IMAGES['hider'] = pygame.image.load('sprites/hider.png').convert_alpha()
    IMAGES['seeker'] = pygame.image.load('sprites/seeker.png').convert_alpha()
    IMAGES['object'] = pygame.image.load('sprites/object.png').convert_alpha()

    HITMASKS['hider'] = getHitmask(IMAGES['hider'])
    HITMASKS['seeker'] = getHitmask(IMAGES['seeker'])

    objects = []
    hiders = []
    seekers = []

    for i in range(1):
        hider = Hider(20, 30, IMAGES['hider'])
        hiders.append(hider)

    for i in range(1):
        seeker = Seeker(200, 200, IMAGES['hider'])
        seekers.append(seeker)

    for i in range(3):
        object = Object(np.random.randint(50, SCREENWIDTH - 50), np.random.randint(50, SCREENHEIGHT - 50))
        objects.append(object)

    run = True
    while run:
        surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))

        surface.blit(IMAGES['background'], (0, 0))

        hider = hiders[0]
        seeker = seekers[0]

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                run = False
                sys.exit()

            #move hider
            if event.type == KEYDOWN and (event.key == K_UP):
                hider.y = hider.y - np.cos(np.deg2rad(hider.angle)) * hider.vel
                hider.x = hider.x - np.sin(np.deg2rad(hider.angle)) * hider.vel
            elif event.type == KEYDOWN and (event.key == K_LEFT):
                hider.angle = hider.angle + hider.rotVel
            elif event.type == KEYDOWN and (event.key == K_RIGHT):
                hider.angle = hider.angle - hider.rotVel

            if hider.x > SCREENWIDTH:
                hider.x = SCREENWIDTH
            if hider.x < 0:
                hider.x = 0
            if hider.y > SCREENHEIGHT:
                hider.y = SCREENHEIGHT
            if hider.y < 0:
                hider.y = 0

            #move seeker
            if event.type == KEYDOWN and (event.key == K_w):
                seeker.y = seeker.y - np.cos(np.deg2rad(seeker.angle)) * seeker.vel
                seeker.x = seeker.x - np.sin(np.deg2rad(seeker.angle)) * seeker.vel
            elif event.type == KEYDOWN and (event.key == K_a):
                seeker.angle = seeker.angle + seeker.rotVel
            elif event.type == KEYDOWN and (event.key == K_d):
                seeker.angle = seeker.angle - seeker.rotVel

            if seeker.x > SCREENWIDTH:
                seeker.x = SCREENWIDTH
            if seeker.x < 0:
                seeker.x = 0
            if seeker.y > SCREENHEIGHT:
                seeker.y = SCREENHEIGHT
            if seeker.y < 0:
                seeker.y = 0

        # draw sprites
        hider.playerSurface = pygame.transform.rotate(IMAGES['hider'], hider.angle)
        for hider in hiders:
            surface.blit(hider.playerSurface, (hider.x, hider.y))

        seeker.playerSurface = pygame.transform.rotate(IMAGES['seeker'], seeker.angle)
        for seeker in seekers:
            surface.blit(seeker.playerSurface, (seeker.x, seeker.y))

        for object in objects:
            surface.blit(IMAGES['object'], (object.x, object.y))

        surfaceScaled = pygame.transform.scale(surface, (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        SCREEN.blit(surfaceScaled, (0, 0))

        #''''
        for seeker in seekers:
            find = seeker.seeHider(hiders)
            if find >= 0:
                hiders.pop(find)
        
        if len(hiders) == 0:
            print("seekers won")
            run = False

        if len(seekers) == 0:
            print("hiders won")
            run = False
        #'''

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


if __name__ == '__main__':
    main()
