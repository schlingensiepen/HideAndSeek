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
from checkpoint import Checkpointer

FPS = 30
SCREENWIDTH = 800
SCREENHEIGHT = 800
SCALING = 1

wSeeker = None
wHider = None
train = 0  # 0 für Seeker 1 für Hider

saver = Checkpointer()

IMAGES = {}
HITMASKS = {}

obstacles_sympy = []
obstacles = []

# spieler können selbst gesteuert werden
debug_mode = False
# es wird angzeigt, was passiert
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
    radius = character.radius

    # check screen borders
    if newx + radius >= SCREENWIDTH or newx - radius < 0 or newy + radius >= SCREENHEIGHT or newy - radius < 0:
        return character.x, character.y

    # check obstacles jetzt neu mit ohne sympy
    for obs in obstacles:
        # links
        if obs.x <= newx + character.radius <= obs.x + obs.width and obs.y <= newy <= obs.y + obs.height:
            return character.x, character.y
        # rechts
        if obs.x + obs.width >= newx - character.radius >= obs.x and obs.y <= newy <= obs.y + obs.height:
            return character.x, character.y

        # oben
        if obs.y <= newy + character.radius <= obs.y + obs.height and obs.x <= newx <= obs.x + obs.width:
            return character.x, character.y

        # unten
        if obs.y + obs.height >= newy - character.radius >= obs.y and obs.x <= newx <= obs.x + obs.width:
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

    if train == 0:
        for i in range(1):
            hider = Hider(200, 60)
            hiders.append(hider)

    if train == 1:
        for i in range(1):
            seeker = Seeker(400, 400)
            seekers.append(seeker)

    for i in range(0):
        obs = Obstacle(np.random.randint(0, SCREENWIDTH - Obstacle.width),
                       np.random.randint(0, SCREENHEIGHT - Obstacle.height))
        obstacles.append(obs)
        sympobs = obs.sympy_obstacle(obs)
        obstacles_sympy.append(sympobs)

    nets = []
    ge = []
    trainNets = []


    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 2100
        if train == 0:
            seeker = Seeker(400, 400)
            trainNets.append(seeker)
        else:
            hider = Hider(60, 60)
            trainNets.append(hider)
            hiders = [hider]
        ge.append(g)

    for x, trained in enumerate(trainNets):
        run = True
        while run:

            if train == 0:
                seeker = trained
                hider = hiders[0]
            else:
                seeker = seekers[0]
                hider = trained

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
                    if train == 0:
                        ge[x].fitness += 200
                    else:
                        ge[x].fitness -= 1500
                    run = False
                elif i[1] == 1:
                    if i[2] < minDis:
                        minDis = i[2]
                        a = i[0]
                        nextHiderY = hiders[a].y
                        nextHiderX = hiders[a].x
                    # see semi
                    see = yellow
                    if train == 0:
                        ge[x].fitness += 1
                    else:
                        ge[x].fitness -= 1

                elif i[1] == 2:
                    if i[2] < minDis:
                        minDis = i[2]
                        a = i[0]
                        nextHiderY = -1
                        nextHiderX = -1
                    # no see
                    see = red

            # wenn seeker trainiert wird
            if train == 0:
                if wHider == None:
                    outputHider = [0, 0]
                else:
                    outputHider = wHider.activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))

                outputSeeker = nets[x].activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))
            # wenn hider trainiert wird
            else:
                if wSeeker == None:
                    outputSeeker = [0, 0]
                else:
                    outputSeeker = wSeeker.activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))
                outputHider = nets[x].activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))

            if graphical_mode:
                # move hider
                if debug_mode:
                    if keys[pygame.K_UP]:
                        hider.x, hider.y = move(hider)
                else:
                    hider.x, hider.y = move(hider)
                if keys[pygame.K_LEFT] or outputHider[0] > 0.5:
                    hider.angle = hider.angle + hider.rotVel
                if keys[pygame.K_RIGHT] or outputHider[1] > 0.5:
                    hider.angle = hider.angle - hider.rotVel
                if hider.angle >= 360:
                    hider.angle -= 360
                if hider.angle <= 0:
                    hider.angle += 360

                # move seeker
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
                surfaceScaled = pygame.transform.scale(surface,
                                                       (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
                SCREEN.blit(surfaceScaled, (0, 0))

                # for object in objects:
                #    surface.blit(IMAGES['object'], (object.x, object.y))

                # hider

                hider.playerSurface = pygame.transform.rotate(IMAGES['hider'], hider.angle)

                for hider in hiders:
                    # surface.blit(hider.playerSurface, (hider.x, hider.y))
                    pygame.draw.circle(SCREEN, blue, [hider.x, hider.y], hider.radius)
                    newx = hider.x - np.sin(np.deg2rad(hider.angle)) * hider.radius
                    newy = hider.y - np.cos(np.deg2rad(hider.angle)) * hider.radius
                    pygame.draw.circle(SCREEN, white, [newx, newy], 5)

                # seeker

                seeker.playerSurface = pygame.transform.rotate(IMAGES['seeker'], seeker.angle)

                # surface.blit(seeker.playerSurface, (seeker.x, seeker.y))
                pygame.draw.circle(SCREEN, red, [seeker.x, seeker.y], seeker.radius)
                newx = seeker.x - np.sin(np.deg2rad(seeker.angle)) * seeker.radius
                newy = seeker.y - np.cos(np.deg2rad(seeker.angle)) * seeker.radius
                pygame.draw.circle(SCREEN, white, [newx, newy], 5)

                # sight visualsisazion

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

                # move hider
                if debug_mode:
                    if keys[pygame.K_UP]:
                        hider.x, hider.y = move(hider)
                else:
                    hider.x, hider.y = move(hider)
                if outputHider[0] > 0.5:
                    hider.angle = hider.angle + hider.rotVel
                if outputHider[1] > 0.5:
                    hider.angle = hider.angle - hider.rotVel
                if hider.angle >= 360:
                    hider.angle -= 360
                if hider.angle <= 0:
                    hider.angle += 360

            loopIter += 1
            if loopIter == 10000:
                run = False
                if train == 0:
                    ge[x].fitness -= 1500
                else:
                    ge[x].fitness += 1500
            if train == 0:
                ge[x].fitness -= 1
            else:
                ge[x].fitness += 1
            # print(ge[x].fitness)















def visResult():
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

    surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
    surface.blit(IMAGES['background'], (0, 0))

    hiders = []
    seekers = []

    for i in range(1):
        hider = Hider(60, 60)
        hiders.append(hider)

    for i in range(1):
        seeker = Seeker(400, 400)
        seekers.append(seeker)

    for i in range(0):
        obs = Obstacle(np.random.randint(0, SCREENWIDTH - Obstacle.width),
                       np.random.randint(0, SCREENHEIGHT - Obstacle.height))
        obstacles.append(obs)
        sympobs = obs.sympy_obstacle(obs)
        obstacles_sympy.append(sympobs)

    run = True
    while run:

        seeker = seekers[0]
        hider = hiders[0]

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                run = False
                sys.exit()

        keys = pygame.key.get_pressed()

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
                run = False
            elif i[1] == 1:
                if i[2] < minDis:
                    minDis = i[2]
                    a = i[0]
                    nextHiderY = hiders[a].y
                    nextHiderX = hiders[a].x
                # see semi
                see = yellow

            elif i[1] == 2:
                if i[2] < minDis:
                    minDis = i[2]
                    a = i[0]
                    nextHiderY = -1
                    nextHiderX = -1
                # no see
                see = red

        # outputs generieren
        outputHider = wHider.activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))
        outputSeeker = wSeeker.activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))

        # move hider
        if debug_mode:
            if keys[pygame.K_UP]:
                hider.x, hider.y = move(hider)
        else:
            hider.x, hider.y = move(hider)
        if keys[pygame.K_LEFT] or outputHider[0] > 0.5:
            hider.angle = hider.angle + hider.rotVel
        if keys[pygame.K_RIGHT] or outputHider[1] > 0.5:
            hider.angle = hider.angle - hider.rotVel
        if hider.angle >= 360:
            hider.angle -= 360
        if hider.angle <= 0:
            hider.angle += 360

        # move seeker
        if not debug_mode:
            nSeekerx, nSeekery = move(seeker)
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
        if keys[pygame.K_d] or outputSeeker[1] > 0.5:
            seeker.angle = seeker.angle - seeker.rotVel
        if seeker.angle >= 360:
            seeker.angle -= 360
        if seeker.angle <= 0:
            seeker.angle += 360

        # draw sprites
        surfaceScaled = pygame.transform.scale(surface,
                                               (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        SCREEN.blit(surfaceScaled, (0, 0))

        # for object in objects:
        #    surface.blit(IMAGES['object'], (object.x, object.y))

        # hider


        for hider in hiders:
            # surface.blit(hider.playerSurface, (hider.x, hider.y))
            pygame.draw.circle(SCREEN, blue, [hider.x, hider.y], hider.radius)
            newx = hider.x - np.sin(np.deg2rad(hider.angle)) * hider.radius
            newy = hider.y - np.cos(np.deg2rad(hider.angle)) * hider.radius
            pygame.draw.circle(SCREEN, white, [newx, newy], 5)

        # seeker

        seeker.playerSurface = pygame.transform.rotate(IMAGES['seeker'], seeker.angle)

        # surface.blit(seeker.playerSurface, (seeker.x, seeker.y))
        pygame.draw.circle(SCREEN, red, [seeker.x, seeker.y], seeker.radius)
        newx = seeker.x - np.sin(np.deg2rad(seeker.angle)) * seeker.radius
        newy = seeker.y - np.cos(np.deg2rad(seeker.angle)) * seeker.radius
        pygame.draw.circle(SCREEN, white, [newx, newy], 5)

        # sight visualsisazion

        pygame.draw.line(SCREEN, see, [seeker.x, seeker.y], [hider.x, hider.y], 2)

        for obstacle in obstacles:
            pygame.draw.rect(SCREEN, black, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

        pygame.display.update()

        loopIter += 1
        # print(ge[x].fitness)

        FPSCLOCK.tick(FPS)




def run(configHider, configSeeker):
    global wSeeker
    global wHider
    global graphical_mode
    global train
    generation_number = 0

    for i in range(100):
        print('Generation: ', generation_number)
        # train Seeker
        saver.start_generation(generation_number)
        train = 0
        configS = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                     configSeeker)

        pS = neat.Population(configS)

        pS.add_reporter(neat.StdOutReporter(True))
        statsS = neat.StatisticsReporter()
        pS.add_reporter(statsS)

        winnerSeeker = pS.run(main, 1)
        wSeeker = neat.nn.FeedForwardNetwork.create(winnerSeeker, configS)
        

        # train Hider
        #graphical_mode = True
    
        train = 1
        configH = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                     configHider)

        pH = neat.Population(configH)

        pH.add_reporter(neat.StdOutReporter(True))
        statsH = neat.StatisticsReporter()
        pH.add_reporter(statsH)

        winnerHider = pH.run(main, 1)
        wHider = neat.nn.FeedForwardNetwork.create(winnerHider, configH)
        generation_number += 1
        saver.end_generation(configH, pH, winnerHider, configS, pS, winnerSeeker)

    input("Press Enter to continue...")

    visResult()


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_pathHider = os.path.join(local_dir, 'configHider.txt')
    config_pathSeeker = os.path.join(local_dir, 'configSeeker.txt')
    run(config_pathHider, config_pathSeeker)
