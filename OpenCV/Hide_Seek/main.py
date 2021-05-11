import pygame
import time
import random
import numpy as np
from sympy import Segment, Polygon, Circle


def run_game():
    pygame.init()

    dis_width = 40
    dis_height = 30

    rendering = True
    time_invervall = 10

    obstacle_number = 20
    obstacles = []
    block_size = 20

    black = (0, 0, 0)
    red = (213, 50, 80)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    white = (255, 255, 255)
    yellow = (255, 255, 102)

    dis = pygame.display.set_mode((dis_width*block_size, dis_height*block_size))
    pygame.display.set_caption('Hide n Seek')

    clock = pygame.time.Clock()


    def move(direction, position):
        newpos = [position[0] + direction[0], position[1] + direction[1]]
        #check screen borders
        if newpos[0] >= dis_width or newpos[0] < 0 or newpos[1] >= dis_height or newpos[1] < 0:
            return position
        #check obstacles
        if newpos in obstacles:
            return position
        return newpos


    #line of sight check
    def look(seeker_pos, hider_pos):
        viewline_center = Segment([(i + 0.5) for i in seeker_pos], [(i + 0.5) for i in hider_pos])
        for i in obstacles:
            obstacle = Polygon(i, (i[0] + 1, i[1]), (i[0] + 1, i[1] + 1), (i[0], i[1] + 1))
            broken_los = viewline_center.intersection(obstacle)           
            if broken_los:
                #print(broken_los)
                return broken_los
        #print('kein hindernis')
        return




    def gameLoop():
        game_over = False
        game_close = False

        centerx = int(dis_width/2)
        centery = int(dis_height/2)

        #seeker starts in screen-center

        seeker_pos = [centerx, centery]

        #hider starts at random position

        hiderx = round(random.randrange(0, dis_width))
        hidery = round(random.randrange(0, dis_height))
        hider_pos = (hiderx, hidery)

        #generate obstacles

        for i in range(obstacle_number):
            obstaclex = round(random.randrange(0, dis_width))
            obstacley = round(random.randrange(0, dis_height))
            ob = [obstaclex, obstacley]
            obstacles.append(ob)


        while not game_over:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print('quitting')
                    game_over = True

            keys = pygame.key.get_pressed()
            #seeker control
            if keys[pygame.K_LEFT]:
                direction = [-1, 0]
                seeker_pos = move(direction, seeker_pos)
            elif keys[pygame.K_RIGHT]:
                direction = [1, 0]
                seeker_pos = move(direction, seeker_pos)
            elif keys[pygame.K_UP]:
                direction = [0, -1]
                seeker_pos = move(direction, seeker_pos)
            elif keys[pygame.K_DOWN]:
                direction = [0, 1]
                seeker_pos = move(direction, seeker_pos)
            
            #finder control
            if keys[pygame.K_a]:
                direction = [-1, 0]
                hider_pos = move(direction, hider_pos)
            elif keys[pygame.K_d]:
                direction = [1, 0]
                hider_pos = move(direction, hider_pos)
            elif keys[pygame.K_w]:
                direction = [0, -1]
                hider_pos = move(direction, hider_pos)
            elif keys[pygame.K_s]:
                direction = [0, 1]
                hider_pos = move(direction, hider_pos)


            viewpath = look(seeker_pos, hider_pos)




            if rendering == True:

                dis.fill(black) 
                #obstacles
                for i in obstacles:
                    pygame.draw.rect(dis, white, [i[0]*block_size, i[1]*block_size, block_size, block_size])
                #seeker
                pygame.draw.circle(dis, red, [(i + 0.5)*block_size for i in seeker_pos], 10)
                #hider
                pygame.draw.circle(dis, green, [(i + 0.5)*block_size for i in hider_pos], 10)
                #vision
                pygame.draw.line(dis, yellow, [(i + 0.5)*block_size for i in seeker_pos], [(i + 0.5)*block_size for i in hider_pos])
                if viewpath:
                    for i in viewpath:
                        pygame.draw.circle(dis, blue, [u*block_size for u in i], 3)

                pygame.display.update()
                clock.tick(time_invervall)

        pygame.quit()
        quit()

    gameLoop()

run_game()