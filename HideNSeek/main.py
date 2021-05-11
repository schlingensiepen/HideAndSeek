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
from obstacle import Obstacle
from sympy import Circle, Segment, Polygon


FPS = 60
SCREENWIDTH = 800
SCREENHEIGHT = 800
SCALING = 1

IMAGES = {}
HITMASKS = {}

obstacles_sympy = []
obstacles = []

red = (213, 50, 80)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 102)
white = (255, 255, 255)
black = (0, 0, 0)

def move(character):

    newx = int(character.x - np.sin(np.deg2rad(character.angle)) * character.vel)
    newy = int(character.y - np.cos(np.deg2rad(character.angle)) * character.vel)
    print(newx, newy)
    radius = character.radius

    #check screen borders   
    if newx+radius >= SCREENWIDTH or newx-radius < 0 or newy+radius >= SCREENHEIGHT or newy-radius < 0:
        return character.x, character.y

    #check obstacles jetzt neu mit ohne sympy
    for obs in obstacles:
        #links
        if obs.x <= newx + character.radius <= obs.x + obs.width and obs.y <= newy <= obs.y + obs.height:
            print('links')
            return character.x, character.y
        #rechts
        if obs.x + obs.width >= newx - character.radius >= obs.x and obs.y <= newy <= obs.y + obs.height:
            print('rechts')
            return character.x, character.y
            
        #oben
        if obs.y <= newy + character.radius <= obs.y + obs.height and obs.x <= newx <= obs.x + obs.width:
            print('oben')
            return character.x, character.y
            
        #unten
        if obs.y  + obs.height >= newy - character.radius >= obs.y and obs.x <= newx <= obs.x + obs.width:
            print('unten')
            return character.x, character.y
            

    '''
    circle = character.draw_circle(newx, newy) 
    for obs in obstacles_sympy:       
        intersect = circle.intersection(obs)
        #print(intersect)
        if intersect:
            return character.x, character.y
    '''
    return newx, newy



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

    
    hiders = []
    seekers = []

    for i in range(1):
        hider = Hider(60, 60, IMAGES['hider'])
        hiders.append(hider)

    for i in range(1):
        seeker = Seeker(400, 400, IMAGES['hider'])
        seekers.append(seeker)

    for i in range(3):
        obs = Obstacle(np.random.randint(0, SCREENWIDTH - Obstacle.width), np.random.randint(0, SCREENHEIGHT - Obstacle.height))
        obstacles.append(obs)
        sympobs = obs.sympy_obstacle(obs)
        obstacles_sympy.append(sympobs)

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

        keys = pygame.key.get_pressed()

        #move hider
        if keys[pygame.K_UP]:
            hider.x, hider.y = move(hider)
        elif keys[pygame.K_LEFT]:
            hider.angle = hider.angle + hider.rotVel
        elif keys[pygame.K_RIGHT]:
            hider.angle = hider.angle - hider.rotVel
        if hider.angle >= 360:
            hider.angle -= 360
        if hider.angle <= 0:
            hider.angle += 360

 
        #move seeker
        if keys[pygame.K_w]:
            seeker.x, seeker.y = move(seeker)
        elif keys[pygame.K_a]:
            seeker.angle = seeker.angle + seeker.rotVel
        elif keys[pygame.K_d]:
            seeker.angle = seeker.angle - seeker.rotVel
        if seeker.angle >= 360:
            seeker.angle -= 360
        if seeker.angle <= 0:
            seeker.angle += 360

        #see hiders  

        see = False
        for seeker in seekers:
            status = seeker.seeHider(hiders, obstacles_sympy)
            for i in status:
                if i[1] == 0:
                    #see
                    see = green
                elif i[1] == 1:   
                    #see semi
                    see = yellow
                elif i[1] == 2:
                    #no see
                    see = red
    
        # draw sprites
        surfaceScaled = pygame.transform.scale(surface, (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        SCREEN.blit(surfaceScaled, (0, 0))

        #for object in objects:
        #    surface.blit(IMAGES['object'], (object.x, object.y))

        #hider

        hider.playerSurface = pygame.transform.rotate(IMAGES['hider'], hider.angle)
        for hider in hiders:
            #surface.blit(hider.playerSurface, (hider.x, hider.y))
            pygame.draw.circle(SCREEN, blue, [hider.x, hider.y], hider.radius)
            newx = hider.x - np.sin(np.deg2rad(hider.angle)) * hider.radius
            newy = hider.y - np.cos(np.deg2rad(hider.angle)) * hider.radius
            pygame.draw.circle(SCREEN, white, [newx, newy], 5)

        #seeker

        seeker.playerSurface = pygame.transform.rotate(IMAGES['seeker'], seeker.angle)
        for seeker in seekers:
            #surface.blit(seeker.playerSurface, (seeker.x, seeker.y))
            pygame.draw.circle(SCREEN, red, [seeker.x, seeker.y], seeker.radius)
            newx = seeker.x - np.sin(np.deg2rad(seeker.angle)) * seeker.radius
            newy = seeker.y - np.cos(np.deg2rad(seeker.angle)) * seeker.radius
            pygame.draw.circle(SCREEN, white, [newx, newy], 5)

         #sight visualsisazion   
        
            pygame.draw.line(SCREEN, see, [seeker.x, seeker.y], [hider.x, hider.y], 2)

        
        for obstacle in obstacles:
            pygame.draw.rect(SCREEN, black, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

        
            
        ''''   
        for seeker in seekers:
            find = seeker.seeHider(hiders)
            if find >= 0:
                print('poop')
                hiders.pop(find)
        
        if len(hiders) == 0:
            print("seekers won")
            run = False

        if len(seekers) == 0:
            print("hiders won")
            run = False
        '''

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
