import pygame
import time
import random
from neat import ai_output
class Snake: 

    def __init__(self, instance):
        self.game_instance = instance + 1
        self.foodx = None
        self.foody = None
        self.snake_Head = None
        self.Length_of_snake = 1
        self.direction = None
    

    def run_game(self):

        pygame.init()

        

        white = (255, 255, 255)
        yellow = (255, 255, 102)
        black = (0, 0, 0)
        red = (213, 50, 80)
        green = (0, 255, 0)
        blue = (50, 153, 213)

        dis_width = 800
        dis_height = 600

        dis = pygame.display.set_mode((dis_width, dis_height))
        pygame.display.set_caption('Snake for PyGame')

        clock = pygame.time.Clock()

        snake_block = 20
        snake_speed = 10


        font_style = pygame.font.SysFont("bahnschrift", 25)
        score_font = pygame.font.SysFont("bahnschrift", 35)

        def output_vector(self):
            headx = int(self.snake_Head[0]/20)
            heady = int(self.snake_Head[1]/20)
            foodx = int(self.foodx/20)
            foody = int(self.foody/20)
            food_dist_x = foodx - headx
            food_dist_y = foody - heady
            score = self.Length_of_snake - 1
            vector = headx, heady, food_dist_x, food_dist_y, score
            return vector

        def Your_score(score):
            value = score_font.render("Your Score: " + str(score), True, red)
            dis.blit(value, [0, 0])


        def our_snake(snake_block, snake_list):
            for x in snake_list:
                pygame.draw.rect(dis, white, [x[0], x[1], snake_block, snake_block])
                pygame.draw.rect(dis, black, [x[0], x[1], snake_block, snake_block], width=1)

        def message(msg, color):
            mesg = font_style.render(msg, True, color)
            dis.blit(mesg, [dis_width / 6, dis_height / 3])

        

        def gameLoop(self):
            game_over = False
            game_close = False

            x1 = dis_width / 2
            y1 = dis_height / 2

            x1_change = 0
            y1_change = 0

            snake_List = []
            

            self.foodx = round(random.randrange(0, dis_width - snake_block) / 20.0) * 20.0
            self.foody = round(random.randrange(0, dis_height - snake_block) / 20.0) * 20.0

            while not game_over:

                while game_close == True:
                    dis.fill(black)
                    message("You Lost! Press C (Play Again) or Q (Quit)", red)
                    message(Your_score(self.Length_of_snake - 1), red)
                    # Your_score(Length_of_snake - 1)
                    pygame.display.update()

                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                game_over = True
                                game_close = False
                            if event.key == pygame.K_c:
                                gameLoop(self)


                

                if self.direction:
                    if self.direction[0] == 1:
                        x1_change = snake_block
                        y1_change = 0
                    if self.direction[0] == -1:
                        x1_change = -snake_block
                        y1_change = 0
                    if self.direction[1] == 1:
                        y1_change = -snake_block
                        x1_change = 0
                    if self.direction[1] == -1:
                        y1_change = snake_block
                        x1_change = 0    

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game_over = True

                    '''   
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            x1_change = -snake_block
                            y1_change = 0
                        elif event.key == pygame.K_RIGHT:
                            x1_change = snake_block
                            y1_change = 0
                        elif event.key == pygame.K_UP:
                            y1_change = -snake_block
                            x1_change = 0
                        elif event.key == pygame.K_DOWN:
                            y1_change = snake_block
                            x1_change = 0
                    '''


                if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
                    game_close = True
                x1 += x1_change
                y1 += y1_change
                dis.fill(black)
                pygame.draw.rect(dis, green, [self.foodx, self.foody, snake_block, snake_block])
                self.snake_Head = []
                self.snake_Head.append(x1)
                self.snake_Head.append(y1)
                snake_List.append(self.snake_Head)
                if len(snake_List) > self.Length_of_snake:
                    del snake_List[0]

                for x in snake_List[:-1]:
                    if x == self.snake_Head:
                        game_close = True

                our_snake(snake_block, snake_List)
                # Your_score(Length_of_snake - 1)

                pygame.display.update()

                if x1 == self.foodx and y1 == self.foody:
                    self.foodx = round(random.randrange(0, dis_width - snake_block) / 20.0) * 20.0
                    self.foody = round(random.randrange(0, dis_height - snake_block) / 20.0) * 20.0
                    self.Length_of_snake += 1

                clock.tick(snake_speed)

                self.direction = ai_output(output_vector(self))
                print('richtung', self.direction)

                

            pygame.quit()
            quit()


        gameLoop(self)