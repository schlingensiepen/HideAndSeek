from itertools import cycle
import random
import sys
from neat import species
import numpy as np
import os
import neat
import pygame
import math
from pygame.locals import *
from hider import Hider
from seeker import Seeker
from obstacle import Obstacle
from checkpoint import Checkpointer


training_Char = 'seeker'  # wer zuerst trainiert wird

# Namen der beiden zu landeneden Checkpoints (erst seeker dann hider) hier rein:
load_checkpoints = ['seeker-neat-checkpoint-2664', 'hider-neat-checkpoint-2664']

# spieler können selbst gesteuert werden
debug_mode = False

# es wird angzeigt, was passiert
graphical_mode = True

#geschwindigkeit im graphical mode cappen
FPS = 200
SCREENWIDTH = 800
SCREENHEIGHT = 800
SCALING = 1

wSeeker = None
wHider = None

saver = Checkpointer()

IMAGES = {}
HITMASKS = {}

obstacles = []

red = (213, 50, 80)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 102)
white = (255, 255, 255)
black = (0, 0, 0)


def obstacle_collision(character, x, y):
    for obs in obstacles:
        # links
        if obs.x <= x + character.radius <= obs.x + obs.width and obs.y <= y <= obs.y + obs.height:
            return True
        # rechts
        if obs.x + obs.width >= x - character.radius >= obs.x and obs.y <= y <= obs.y + obs.height:
            return True
        # oben
        if obs.y <= y + character.radius <= obs.y + obs.height and obs.x <= x <= obs.x + obs.width:
            return True           
        # unten
        if obs.y + obs.height >= y - character.radius >= obs.y and obs.x <= x <= obs.x + obs.width:
            return True
    return False


def move(character):
    newx = int(character.x - np.sin(np.deg2rad(character.angle)) * character.vel)
    newy = int(character.y - np.cos(np.deg2rad(character.angle)) * character.vel)
    radius = character.radius

    # check screen borders
    if newx + radius >= SCREENWIDTH or newx - radius < 0 or newy + radius >= SCREENHEIGHT or newy - radius < 0:
        return character.x, character.y

    # check obstacles  
    collision = obstacle_collision(character, newx, newy)
    if collision == True:
        return character.x, character.y

    return newx, newy


#vision, bestehend aus 8 'Strahlen'
def seethings(character):
    x = character.x
    y = character.y

    #senkrecht
    dist_up_wall = y
    dist_down_wall = SCREENHEIGHT - y
    uppoint = (x, 0)
    downpoint = (x, SCREENHEIGHT)
    dist_up = dist_up_wall
    dist_down = dist_down_wall  
    for obs in obstacles:
        if  obs.x <= x <= obs.x + obs.width:
            dist = obs.y - y           
            if dist > 0 and dist < dist_down:
                dist_down = dist
                downpoint = (x, obs.y)
            elif dist < 0 and abs(dist) < dist_up:
                dist_up = abs(dist + obs.height)
                uppoint = (x, obs.y + obs.height)

    #waagrecht
    dist_left_wall = x
    dist_right_wall = SCREENWIDTH - x
    leftpoint = (0, y)
    rightpoint = (SCREENWIDTH, y)
    dist_left = dist_left_wall
    dist_right = dist_right_wall
    for obs in obstacles:
        if  obs.y <= y <= obs.y + obs.height:
            dist = obs.x - x
            if dist < 0 and dist < dist_left:
                dist_left = abs(dist) - obs.width
                leftpoint = (obs.x + obs.width, y)
            if dist > 0 and abs(dist) < dist_right:
                dist_right = abs(dist)
                rightpoint = (obs.x, y)
  
    #schräg aufsteigend
    if SCREENHEIGHT - y < x:
        dist_lowleft = math.sqrt(2) * dist_down_wall
        lowleftpoint = (x - dist_down_wall, y + dist_down_wall)
    else:
        dist_lowleft = math.sqrt(2) * dist_left_wall
        lowleftpoint = (x - dist_left_wall, y + dist_left_wall)
       
    if y < SCREENWIDTH - x:
        dist_upright = math.sqrt(2) * dist_up_wall
        uprightpoint = (x + dist_up_wall, y - dist_up_wall)
    else:
        dist_upright = math.sqrt(2) * dist_right_wall
        uprightpoint = (x + dist_right_wall, y - dist_right_wall)

    #schräg fallend
    if x < y:
        dist_upleft = math.sqrt(2) * dist_left_wall
        upleftpoint = (x - dist_left_wall, y - dist_left_wall)
    else:
        dist_upleft = math.sqrt(2) * dist_up_wall
        upleftpoint = (x - dist_up_wall, y - dist_up_wall)

    if SCREENWIDTH - x < SCREENHEIGHT - y:
        dist_lowright = math.sqrt(2) * dist_right_wall
        lowrightpoint = (x + dist_right_wall, y + dist_right_wall)
    else:
        dist_lowright = math.sqrt(2) * dist_down_wall
        lowrightpoint = (x + dist_down_wall, y + dist_down_wall)


    for obs in obstacles:       
        dist_x = obs.x - x
        dist_y = obs.y - y
        if abs(dist_x) < abs(dist_y):
            shorterdist = abs(dist_x)
        else:
            shorterdist = abs(dist_y)

        #unten links
        #ist das Hindernis links unten, vom char aus gesehen?
        if dist_x < 0 and dist_y > 0:

            #wäre der zu rechnende Punkt überhaupt näher?
            if math.sqrt(2) * shorterdist < dist_lowleft:
                obs_point_waagrecht = [x - dist_y, obs.y]
                obs_point_senkrecht = [obs.x + obs.width, y - (dist_x + obs.width)]

                #trifft die Linie auf die nahe, waagrechte Seite des hindernisses?
                if obs.x <= obs_point_waagrecht[0] <= obs.x + obs.width:
                    dist_lowleft = math.sqrt(2) * shorterdist
                    lowleftpoint = obs_point_waagrecht

                #trifft die Linie auf die nahe, seknrechte Seite des hindernisses?                
                elif obs.y <= obs_point_senkrecht[1] <= obs.y + obs.height:
                    dist_lowleft = math.sqrt(2) * shorterdist
                    lowleftpoint = obs_point_senkrecht
            
        #oben rechts
        if dist_x + obs.width > 0 and dist_y < 0:

            if math.sqrt(2) * shorterdist < dist_upright:
                obs_point_waagrecht = [x - dist_y - obs.height, obs.y + obs.height]
                obs_point_senkrecht = [obs.x, y - dist_x]
                
                if obs.x <= obs_point_waagrecht[0] <= obs.x + obs.width:
                    dist_upright = math.sqrt(2) * (shorterdist - obs.height)
                    uprightpoint = obs_point_waagrecht

                elif obs.y <= obs_point_senkrecht[1] <= obs.y + obs.height:
                    dist_upright = math.sqrt(2) * (shorterdist - obs.height)
                    uprightpoint = obs_point_senkrecht
        
        #oben links
        if dist_x < 0 and dist_y < 0:

            if math.sqrt(2) * shorterdist < dist_upleft:
                obs_point_waagrecht = [x + dist_y + obs.height, obs.y + obs.height]
                obs_point_senkrecht = [obs.x + obs.width, y + dist_x + obs.width]

                if obs.x <= obs_point_waagrecht[0] <= obs.x + obs.width:
                    dist_upleft = math.sqrt(2) * (shorterdist - obs.height)
                    upleftpoint = obs_point_waagrecht
                
                elif obs.y <= obs_point_senkrecht[1] <= obs.y + obs.height:
                    dist_upleft = math.sqrt(2) * (shorterdist - obs.height)
                    upleftpoint = obs_point_senkrecht

        #unten rechts
        if dist_x + obs.width > 0 and dist_y > 0:

            if math.sqrt(2) * shorterdist < dist_lowright:
                obs_point_waagrecht = [x + dist_y, obs.y]
                obs_point_senkrecht = [obs.x, y + dist_x]

                if obs.x <= obs_point_waagrecht[0] <= obs.x + obs.width:
                    dist_lowright = math.sqrt(2) * shorterdist
                    lowrightpoint = obs_point_waagrecht
                
                elif obs.y <= obs_point_senkrecht[1] <= obs.y + obs.height:
                    dist_lowright = math.sqrt(2) * shorterdist
                    lowrightpoint = obs_point_senkrecht
                          
    pointslist = [uppoint, downpoint, leftpoint, rightpoint, lowleftpoint, uprightpoint, upleftpoint, lowrightpoint]
    distlist = [dist_up, dist_down, dist_left, dist_right, int(dist_lowleft), int(dist_upright), int(dist_upleft), int(dist_lowright)]

    return pointslist, distlist

def main_seeker(seekergenomes, seekerconfig):
    wSeeker = main(seekergenomes, seekerconfig, 'seeker')
    return wSeeker

def main_hider(hidergenomes, hiderconfig):
    winnerHider = main(hidergenomes, hiderconfig, 'hider')
    return winnerHider


def main(genomes, config, trainedChar):
    training_Char = trainedChar
 
    if graphical_mode:
        global SCREEN, FPSCLOCK
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
        pygame.display.set_caption('Hide and Seek')
        pygame.font.init()
        myfont = pygame.font.SysFont('Calibri', 25)

        IMAGES['background'] = pygame.image.load('sprites/bg.png').convert_alpha()

        surface = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
        surface.blit(IMAGES['background'], (0, 0))
        

    hiders = []
    seekers = []
    
    if training_Char == 'seeker':
        for i in range(1):
            hider = Hider()

    if training_Char == 'hider':
        for i in range(1):
            seeker = Seeker()
    
    obstacles.clear()
    for i in range(3):
        obs = Obstacle(np.random.randint(0, SCREENWIDTH - Obstacle.width),
                       np.random.randint(0, SCREENHEIGHT - Obstacle.height))
        obstacles.append(obs)
   


    seeker_los_color = red
    hider_los_color = red

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        genome.fitness = 20000
 
        if training_Char == 'seeker':
            seeker = Seeker()

        else:
            hider = Hider()

        loopIter = 0
        run = True

        #Spieler sollen nicht in Hindernissen spawnen (funktion fraglich)
        #setzt aber auf jeden fall eine zufällige Position
        hider_in_obstacle = True
        while hider_in_obstacle == True:
            hider.x = np.random.randint(hider.radius, SCREENWIDTH - hider.radius)
            hider.y = np.random.randint(hider.radius, SCREENHEIGHT - hider.radius)
            hider_in_obstacle = obstacle_collision(hider, hider.x, hider.y)
        hider.angle = np.random.randint(0, 360)

        seeker_in_obstacle = True
        while seeker_in_obstacle == True:
            seeker.x = np.random.randint(seeker.radius, SCREENWIDTH - seeker.radius)
            seeker.y = np.random.randint(seeker.radius, SCREENHEIGHT - seeker.radius)
            seeker_in_obstacle = obstacle_collision(seeker, seeker.x, seeker.y)
        seeker.angle = np.random.randint(0, 360)
        

        #Gameloop
        while run:

            if graphical_mode:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        run = False
                        sys.exit()
               
            else:
                event = False

            # who sees who
            hiders = [hider]
            # prüft was gesehen wird
            status = seeker.see(hiders, obstacles)
            hiderangle = -1
            seekerangle = -1
            for sublist in status:
                hider = sublist[0]
                # seeker found hider
                if sublist[1] == 'seeker_see':
                    seeker_los_color = green
                    hider_los_color = green
                    nextHiderY = hider.y
                    nextHiderX = hider.x
                    hiderangle = hider.angle
                    if training_Char == 'seeker':
                        genome.fitness += 20000
                    else:
                        genome.fitness -= 20000
                    run = False
                    print('hider gefunden')

                # seeker sees hider
                elif sublist[1] == 'seeker_seesemi':
                    seeker_los_color = yellow                   
                    nextHiderY = hider.y
                    nextHiderX = hider.x
                    hiderangle = hider.angle
                    if training_Char == 'seeker':
                        genome.fitness += 30
                    else:
                        genome.fitness -= 1
                # seeker does not see hider
                else:
                    seeker_los_color = red
                    nextHiderY = -1
                    nextHiderX = -1

                #hider see seeker
                if sublist[2] == 'hider_see':
                    hider_los_color = yellow
                    nextSeekerX = seeker.x
                    nextSeekerY = seeker.y
                    seekerangle = seeker.angle
                    if training_Char == 'hider':
                        genome.fitness += 1

                #hider nosee
                else:
                    hider_los_color = red
                    nextSeekerX = -1
                    nextSeekerY = -1

            #lidarlike sicht
            debugpoints_seeker = []
            debugpoints_seeker, seekervision = seethings(seeker)
            debugpoints_hider, hidervision = seethings(hider)

            #vollständige inputs
            seekerinputs = [seeker.x, seeker.y, seeker.angle, hiderangle, nextHiderX, nextHiderY]
            for entry in seekervision:
                seekerinputs.append(entry)

            hiderinputs = [hider.x, hider.y, hider.angle, seekerangle, nextSeekerX, nextSeekerY]
            for entry in seekervision:
                hiderinputs.append(entry)

            # wenn seeker trainiert wird
            if training_Char == 'seeker':
                if wHider == None:
                    outputHider = [0, 0, 0]
                else:
                    outputHider = wHider.activate(hiderinputs)

                outputSeeker = net.activate(seekerinputs)

            # wenn hider trainiert wird
            else:
                if wSeeker == None:
                    outputSeeker = [0, 0, 0]
                else:
                    outputSeeker = wSeeker.activate(seekerinputs)

                outputHider = net.activate(hiderinputs)

            # manuelle Steuerung

            if debug_mode:
                keys = pygame.key.get_pressed()
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
            else:
                seekeraction = False
                hideraction = False
                # Seeker
                if outputSeeker[0] > 0.5:
                    if training_Char == 'seeker':
                        genome.fitness += 10
                    seekeraction = True
                    nSeekerx, nSeekery = move(seeker)
                    if nSeekerx == seeker.x and nSeekery == seeker.y:
                        if training_Char == 'seeker':
                            genome.fitness -= 5
                            #loopIter += 30
                    seeker.x = nSeekerx
                    seeker.y = nSeekery

                if outputSeeker[1] > 0.5:
                    seekeraction = True
                    seeker.angle = seeker.angle + seeker.rotVel

                if outputSeeker[2] > 0.5:
                    seekeraction = True
                    seeker.angle = seeker.angle - seeker.rotVel
 

                if seeker.angle >= 360:
                    seeker.angle -= 360
                if seeker.angle <= 0:
                    seeker.angle += 360
                           

                # Hider
                if outputHider[0] > 0.5:
                    if training_Char == 'hider':
                        genome.fitness += 10
                    hideraction = True
                    nHiderx, nHidery = move(hider)
                    if nHiderx == hider.x and nHidery == hider.y:
                        if training_Char == 'hider':
                            genome.fitness -= 5
                    hider.x = nHiderx
                    hider.y = nHidery

                if outputHider[1] > 0.5:
                    hideraction = True
                    hider.angle = hider.angle + hider.rotVel

                if outputHider[2] > 0.5:
                    hideraction = True
                    hider.angle = hider.angle - hider.rotVel


                if hider.angle >= 360:
                    hider.angle -= 360
                if hider.angle <= 0:
                    hider.angle += 360

                #strafe fürs nichts tun
                if training_Char == 'seeker':
                    if seekeraction == False:
                        genome.fitness -= 50
                    else:
                        genome.fitness += 0.5
                else:
                    if hideraction == False:
                        genome.fitness -= 50
                    else:
                        genome.fitness += 0.5

            # GUI, falls gewollt
            if graphical_mode:

                # background
                surfaceScaled = pygame.transform.scale(surface,
                                                       (int(SCREENWIDTH * SCALING), int(SCREENHEIGHT * SCALING)))
                SCREEN.blit(surfaceScaled, (0, 0))

                #text
                if training_Char == 'seeker':
                    text_color = red
                else:
                    text_color = green
                text = '{0}{1}'.format('trainiert: ', training_Char)
                textsurface = myfont.render((text), False, text_color)
                SCREEN.blit(textsurface,(0,0))

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

                # line of sight
                deltaX = hider.x - seeker.x
                deltaY = hider.y - seeker.y
                los_middle = [seeker.x + deltaX/2, seeker.y + deltaY/2]
                pygame.draw.line(SCREEN, seeker_los_color, [seeker.x, seeker.y], los_middle, 2)
                pygame.draw.line(SCREEN, hider_los_color, [hider.x, hider.y], los_middle, 2)

                #vision
                if debugpoints_seeker:
                    for point in debugpoints_seeker:
                        pygame.draw.line(SCREEN, blue, [seeker.x, seeker.y], [point[0], point[1]])
                if debugpoints_hider:
                    for point in debugpoints_hider:
                        pygame.draw.line(SCREEN, blue, [hider.x, hider.y], [point[0], point[1]])

                # obstacles
                for obstacle in obstacles:
                    pygame.draw.rect(SCREEN, black, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

                pygame.display.update()
                FPSCLOCK.tick(FPS)

            loopIter += 1
            if loopIter >= 5000:
                print('Zeit abgelaufen')
                if training_Char == 'seeker':
                    genome.fitness -= 20000
                else:
                    genome.fitness += 20000
                run = False

            if training_Char == 'seeker':
                genome.fitness -= 5
            else:
                genome.fitness += 0.5
            #print(genome.fitness)

'''
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
        status = seeker.see(hiders, obstacles)
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

        pygame.draw.line(SCREEN, los_color, [seeker.x, seeker.y], [hider.x, hider.y], 2)

        for obstacle in obstacles:
            pygame.draw.rect(SCREEN, black, [obstacle.x, obstacle.y, obstacle.width, obstacle.height])

        pygame.display.update()

        loopIter += 1
        # print(ge[x].fitness)

        FPSCLOCK.tick(FPS)
'''

def train(configFileSeeker, configFileHider):
    global wSeeker
    global wHider
    global graphical_mode
    global training_Char
    
    
    if load_checkpoints:
        print('\nrestoring Checkpoints...')
        try:   
            seekercheckpoint = saver.restore_checkpoint(load_checkpoints[0])
            hidercheckpoint = saver.restore_checkpoint(load_checkpoints[1])
            pS = seekercheckpoint
            pH = hidercheckpoint
            configS = pS.config
            configH = pH.config
            print('Checkpoints geladen')
        except:
            print('Checkpoints not found')
            configS = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                     configFileSeeker)
            configH = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                     configFileHider)            
            pS = neat.Population(configS)
            pH = neat.Population(configH)
    
    
    pS.add_reporter(neat.StdOutReporter(True))
    statsS = neat.StatisticsReporter()
    pS.add_reporter(statsS)

    pH.add_reporter(neat.StdOutReporter(True))
    statsH = neat.StatisticsReporter()
    pH.add_reporter(statsH)

    #loop für abwechselndes trainieren
    while True:
      
        saver.start_generation(pS.generation)

        # train Seeker
        if training_Char == 'seeker':              
            winnerSeeker = pS.run(main_seeker, 1)
            wSeeker = neat.nn.FeedForwardNetwork.create(winnerSeeker, configS)
            training_Char = 'hider'    
            

        # train Hider
        else:             
            winnerHider = pH.run(main_hider, 1)
            wHider = neat.nn.FeedForwardNetwork.create(winnerHider, configH)
            training_Char = 'seeker'   

        saver.end_generation( pS.config, pS.population, pS.species, pH.config, pH.population, pH.species)



if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_pathSeeker = os.path.join(local_dir, 'configSeeker.txt')
    config_pathHider = os.path.join(local_dir, 'configHider.txt')
    train(config_pathSeeker, config_pathHider)