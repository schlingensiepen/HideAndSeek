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


FPS = 10000
SCREENWIDTH = 800
SCREENHEIGHT = 800
SCALING = 1

IMAGES = {}
HITMASKS = {}

obstacles_sympy = []
obstacles = []

debug_mode = False
graphical_mode = True

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



def main(genomes, config):
    score = loopIter = 0

    global SCREEN, FPSCLOCK


    if graphical_mode:
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        pygame.display.set_caption('Hide and Seek')

        IMAGES['background'] = pygame.image.load('sprites/bg.png').convert_alpha()
        IMAGES['hider'] = pygame.image.load('sprites/hider.png').convert_alpha()
        IMAGES['seeker'] = pygame.image.load('sprites/seeker.png').convert_alpha()
        IMAGES['object'] = pygame.image.load('sprites/object.png').convert_alpha()

        surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
        surface.blit(IMAGES['background'], (0, 0))

    
    hiders = []
    seekers = []

    for i in range(1):
        hider = Hider(60, 60)
        hiders.append(hider)

    '''for i in range(1):
        seeker = Seeker(400, 400, IMAGES['hider'])
        seekers.append(seeker)'''

    for i in range(0):
        obs = Obstacle(np.random.randint(0, SCREENWIDTH - Obstacle.width), np.random.randint(0, SCREENHEIGHT - Obstacle.height))
        obstacles.append(obs)
        sympobs = obs.sympy_obstacle(obs)
        obstacles_sympy.append(sympobs)

    nets = []
    ge = []
    seekerNets = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 2100
        seeker = Seeker(400, 400)
        seekerNets.append(seeker)
        ge.append(g)

    for x, seeker in enumerate(seekerNets):
        print("new")
        run = True
        while run:

            hider = hiders[0]

            if graphical_mode:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        run = False
                        sys.exit()

                keys = pygame.key.get_pressed()
            else:
                event = False
                keys = None

            # see hiders
            see = False
            nextHiderX = -1
            nextHiderY = -1
            minDis = 100000
            status = seeker.seeHider(hiders, obstacles_sympy)
            for i in status:
                if i[1] == 0:
                    if i[2] < minDis:
                        minDis = i[2]
                        a = i[0]
                        nextHiderY = hiders[a].y
                        nextHiderX = hiders[a].x
                    # see
                    see = green
                    ge[x].fitness += 200
                    run = False
                elif i[1] == 1:
                    if i[2] < minDis:
                        minDis = i[2]
                        a = i[0]
                        nextHiderY = hiders[a].y
                        nextHiderX = hiders[a].x
                    # see semi
                    see = yellow
                    ge[x].fitness += 1

                elif i[1] == 2:
                    if i[2] < minDis:
                        minDis = i[2]
                        a = i[0]
                        nextHiderY = -1
                        nextHiderX = -1
                    # no see
                    see = red

            if not debug_mode:
                outputSeeker = nets[x].activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))
            else:
                outputSeeker = [0,0,0]



            if graphical_mode:
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
                if not debug_mode:
                    nSeekerx, nSeekery = move(seeker)
                    ge[x].fitness += 0.1
                    if nSeekerx == seeker.x and nSeekery == seeker.y:
                        ge[x].fitness -= 1000
                        run = False
                    seeker.x = nSeekerx
                    seeker.y = nSeekery
                else:
                    if keys[pygame.K_w]:
                        seeker.x, seeker.y = move(seeker)
                if keys[pygame.K_a] or outputSeeker[0] > 0.5:
                    seeker.angle = seeker.angle + seeker.rotVel
                    ge[x].fitness += 0.1
                if keys[pygame.K_d] or outputSeeker[1] > 0.5:
                    seeker.angle = seeker.angle - seeker.rotVel
                    ge[x].fitness += 0.1
                if seeker.angle >= 360:
                    seeker.angle -= 360
                if seeker.angle <= 0:
                    seeker.angle += 360


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

                #surface.blit(seeker.playerSurface, (seeker.x, seeker.y))
                pygame.draw.circle(SCREEN, red, [seeker.x, seeker.y], seeker.radius)
                newx = seeker.x - np.sin(np.deg2rad(seeker.angle)) * seeker.radius
                newy = seeker.y - np.cos(np.deg2rad(seeker.angle)) * seeker.radius
                pygame.draw.circle(SCREEN, white, [newx, newy], 5)

                #sight visualsisazion

                pygame.draw.line(SCREEN, see, [seeker.x, seeker.y], [hider.x, hider.y], 2)


                for obstacle in obstacles:
                    pygame.draw.rect(SCREEN, black, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

                pygame.display.update()
            else:
                # move seeker

                nSeekerx, nSeekery = move(seeker)
                ge[x].fitness += 0.1
                if nSeekerx == seeker.x and nSeekery == seeker.y:
                    ge[x].fitness -= 1000
                    run = False
                seeker.x = nSeekerx
                seeker.y = nSeekery
                if outputSeeker[0] > 0.5:
                    seeker.angle = seeker.angle + seeker.rotVel
                    ge[x].fitness += 0.1
                if outputSeeker[1] > 0.5:
                    seeker.angle = seeker.angle - seeker.rotVel
                    ge[x].fitness += 0.1
                if seeker.angle >= 360:
                    seeker.angle -= 360
                if seeker.angle <= 0:
                    seeker.angle += 360

            loopIter += 1
            if loopIter == 1000:
                run = False
                ge[x].fitness -= 1500
            ge[x].fitness -= 1
            print(ge[x].fitness)

            if graphical_mode:
                FPSCLOCK.tick(FPS)


def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configSeeker.txt')
    run(config_path)