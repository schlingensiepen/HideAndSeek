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

FPS = 60
SCREENWIDTH = 800
SCREENHEIGHT = 800
SCALING = 1

wSeeker = None
wHider = None
train = 0  # 0 für Seeker 1 für Hider

# Namen der beiden zu landeneden Checkpoints (erst seeker dann hider) hier rein:
load_checkpoints = ['seeker-neat-checkpoint-2', 'hider-neat-checkpoint-2']

# spieler können selbst gesteuert werden
debug_mode = False

# es wird angzeigt, was passiert
graphical_mode = True

saver = Checkpointer()

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
        hider.x = np.random.randint(hider.radius, SCREENWIDTH - hider.radius)
        hider.y = np.random.randint(hider.radius, SCREENHEIGHT - hider.radius)
        hider.angle = np.random.randint(0, 360)
        seeker.x = np.random.randint(seeker.radius, SCREENWIDTH - seeker.radius)
        seeker.y = np.random.randint(seeker.radius, SCREENHEIGHT - seeker.radius)
        seeker.angle = np.random.randint(0, 360)
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

            # prüft was gesehen wird
            status = seeker.seeHider(hiders, obstacles_sympy)
            for i in status:

                # see
                if i[1] == 0:
                    see = green
                    a = i[0]
                    nextHiderY = hiders[a].y
                    nextHiderX = hiders[a].x
                    if train == 0:
                        ge[x].fitness += 200
                    else:
                        ge[x].fitness -= 2000
                    run = False

                # see semi
                elif i[1] == 1:
                    see = yellow
                    a = i[0]
                    nextHiderY = hiders[a].y
                    nextHiderX = hiders[a].x
                    if train == 0:
                        ge[x].fitness += 1
                    else:
                        ge[x].fitness -= 1

                # no see
                elif i[1] == 2:
                    see = red
                    a = i[0]
                    nextHiderY = -1
                    nextHiderX = -1

            # wenn seeker trainiert wird
            if train == 0:
                if wHider == None:
                    outputHider = [0, 0]
                else:
                    outputHider = wHider.activate((hider.x, hider.y, hider.angle, seeker.angle, seeker.x, seeker.y))

                outputSeeker = nets[x].activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))

            # wenn hider trainiert wird
            else:
                if wSeeker == None:
                    outputSeeker = [0, 0]
                else:
                    outputSeeker = wSeeker.activate((seeker.x, seeker.y, seeker.angle, nextHiderX, nextHiderY))
                outputHider = nets[x].activate((hider.x, hider.y, hider.angle, seeker.angle, seeker.x, seeker.y))

            # manuelle Steuerung

            if debug_mode:
                # Seeker
                if keys[pygame.K_UP]:
                    seeker.x, seeker.y = move(seeker)
                if keys[pygame.K_LEFT]:
                    seeker.angle = seeker.angle + seeker.rotVel
                elif keys[pygame.K_RIGHT]:
                    seeker.angle = seeker.angle - seeker.rotVel
                if seeker.angle >= 360:
                    seeker.angle -= 360
                if seeker.angle <= 0:
                    seeker.angle += 360

                # Hider
                if keys[pygame.K_w]:
                    hider.x, hider.y = move(hider)
                if keys[pygame.K_a]:
                    hider.angle = hider.angle + hider.rotVel
                elif keys[pygame.K_d]:
                    hider.angle = hider.angle - hider.rotVel
                if hider.angle >= 360:
                    hider.angle -= 360
                if hider.angle <= 0:
                    hider.angle += 360

                # Movement durch KI
                # Seeker
            else:
                # Seeker
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
                nSeekerx, nSeekery = move(seeker)
                ge[x].fitness += 0.1
                if nSeekerx == seeker.x and nSeekery == seeker.y:
                    print('seeker hängt fest')
                    if train == 0:
                        ge[x].fitness -= 500
                    run = False
                seeker.x = nSeekerx
                seeker.y = nSeekery

                # Hider

                if outputHider[0] > 0.5:
                    hider.angle = hider.angle + hider.rotVel
                if outputHider[1] > 0.5:
                    hider.angle = hider.angle - hider.rotVel
                if hider.angle >= 360:
                    hider.angle -= 360
                if hider.angle <= 0:
                    hider.angle += 360

                hider.x, hider.y = move(hider)

            # GUI, falls gewollt
            if graphical_mode:

                # background
                surfaceScaled = pygame.transform.scale(surface,
                                                       (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
                SCREEN.blit(surfaceScaled, (0, 0))

                # hider
                pygame.draw.circle(SCREEN, blue, [hider.x, hider.y], hider.radius)
                newx = hider.x - np.sin(np.deg2rad(hider.angle)) * hider.radius
                newy = hider.y - np.cos(np.deg2rad(hider.angle)) * hider.radius
                pygame.draw.circle(SCREEN, white, [newx, newy], 5)

                # seeker
                pygame.draw.circle(SCREEN, red, [seeker.x, seeker.y], seeker.radius)
                newx = seeker.x - np.sin(np.deg2rad(seeker.angle)) * seeker.radius
                newy = seeker.y - np.cos(np.deg2rad(seeker.angle)) * seeker.radius
                pygame.draw.circle(SCREEN, white, [newx, newy], 5)

                # line of sight visualsisazion
                pygame.draw.line(SCREEN, see, [seeker.x, seeker.y], [hider.x, hider.y], 2)

                # obstacles
                for obstacle in obstacles:
                    pygame.draw.rect(SCREEN, black, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

                pygame.display.update()

            loopIter += 1
            if loopIter == 5000:
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

            # see
            if i[1] == 0:
                see = green
                a = i[0]
                nextHiderY = hiders[a].y
                nextHiderX = hiders[a].x
                run = False

            # see semi
            elif i[1] == 1:
                see = yellow
                a = i[0]
                nextHiderY = hiders[a].y
                nextHiderX = hiders[a].x

            # no see
            elif i[1] == 2:
                see = red
                a = i[0]
                nextHiderY = -1
                nextHiderX = -1

        # outputs generieren
        outputHider = wHider.activate((hider.x, hider.y, hider.angle, seeker.angle, seeker.x, seeker.y))
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
    '''if load_checkpoints:
        print('\n restoring Checkpoints...')
        seekercheckpoint = saver.restore_checkpoint(load_checkpoints[0])
        hidercheckpoint = saver.restore_checkpoint(load_checkpoints[1])
        print(seekercheckpoint, hidercheckpoint)'''

    for i in range(200):
        print('\n Generation: ', generation_number)
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

        winnerSeeker = pS.run(main, 50)
        wSeeker = neat.nn.FeedForwardNetwork.create(winnerSeeker, configS)

        # train Hider
        train = 1
        configH = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                     configHider)

        pH = neat.Population(configH)

        pH.add_reporter(neat.StdOutReporter(True))
        statsH = neat.StatisticsReporter()
        pH.add_reporter(statsH)

        winnerHider = pH.run(main, 50)
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