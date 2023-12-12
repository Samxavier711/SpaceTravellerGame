

import neat
# import visualize
import pickle
import pygame
import random
import os
import time
pygame.font.init()  # init font

width = 600
height = 800
floor = 730
statfont = pygame.font.SysFont("comicsans", 50)
endfont = pygame.font.SysFont("comicsans", 70)
draw_lines = False

win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Space traveller 1D Motion")

bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x_val) + ".png"))) for x_val in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())
pole_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
background = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.jpeg")).convert_alpha(), (600, 900))


gen = 0

class Bird:
   
    maximum_rotation = 25
    images = bird_images
    rotationval = 20
    time_duration = 5

    def __init__(self, x_val, y_val):
        
        self.x_val = x_val
        self.y_val = y_val
        self.tilt = 0  # degrees to tilt
        self.tick_cnt = 0
        self.vel = 0
        self.height = self.y_val
        self.image_cnt = 0
        self.image = self.images[0]

    def jump(self):
       
        self.vel = -10.5
        self.tick_cnt = 0
        self.height = self.y_val

    def move(self):
        
        self.tick_cnt += 1

        # for downward acceleration
        distance = self.vel*(self.tick_cnt) + 0.5*(3)*(self.tick_cnt)**2  # calculate distance

        # terminal velocity
        if distance >= 16:
            distance = (distance/abs(distance)) * 16

        if distance < 0:
            distance -= 2

        self.y_val = self.y_val + distance

        if distance < 0 or self.y_val < self.height + 50:  # tilt up
            if self.tilt < self.maximum_rotation:
                self.tilt = self.maximum_rotation
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.rotationval

    def draw(self, win):
       
        self.image_cnt += 1

        # For animation of bird, loop through three images
        if self.image_cnt <= self.time_duration:
            self.image = self.images[0]
        elif self.image_cnt <= self.time_duration*2:
            self.image = self.images[1]
        elif self.image_cnt <= self.time_duration*3:
            self.image = self.images[2]
        elif self.image_cnt <= self.time_duration*4:
            self.image = self.images[1]
        elif self.image_cnt == self.time_duration*4 + 1:
            self.image = self.images[0]
            self.image_cnt = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.image = self.images[1]
            self.image_cnt = self.time_duration*2


        # tilt the bird
        blitRotateCenter(win, self.image, (self.x_val, self.y_val), self.tilt)

    def get_mask(self):
       
        return pygame.mask.from_surface(self.image)


class Pole():
   
    gap = 200
    VEL = 5

    def __init__(self, x_val):
        
        self.x_val = x_val
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pole_img, False, True)
        self.PIPE_BOTTOM = pole_img

        self.passed = False

        self.set_height()

    def set_height(self):
        
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
       
        self.x_val -= self.VEL

    def draw(self, win):
      
        # draw top
        win.blit(self.PIPE_TOP, (self.x_val, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x_val, self.bottom))


    def collide(self, bird, win):
       
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x_val - bird.x_val, self.top - round(bird.y_val))
        bottom_offset = (self.x_val - bird.x_val, self.bottom - round(bird.y_val))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
   
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y_val):
       
        self.y_val = y_val
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
       
        win.blit(self.IMG, (self.x1, self.y_val))
        win.blit(self.IMG, (self.x2, self.y_val))


def blitRotateCenter(surf, image, topleft, angle):
   
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
  
    if gen == 0:
        gen = 1
    win.blit(background, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        if draw_lines:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x_val+bird.image.get_width()/2, bird.y_val + bird.image.get_height()/2), (pipes[pipe_ind].x_val + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x_val+bird.image.get_width()/2, bird.y_val + bird.image.get_height()/2), (pipes[pipe_ind].x_val + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = statfont.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (width - score_label.get_width() - 15, 10))

    # generations
    score_label = statfont.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = statfont.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
  
    global win, gen
    win = win
    gen += 1

   
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(floor)
    pipes = [Pole(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x_val > pipes[0].x_val + pipes[0].PIPE_TOP.get_width():  
                pipe_ind = 1                                                                 

        for x_val, bird in enumerate(birds):  
            ge[x_val].fitness += 0.1
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y_val, abs(bird.y_val - pipes[pipe_ind].height), abs(bird.y_val - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x_val + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x_val < bird.x_val:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pole(width))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y_val + bird.image.get_height() - 10 >= floor or bird.y_val < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(win, birds, pipes, base, score, gen, pipe_ind)

       


def run(config_file):
   
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
   
    winner = p.run(eval_genomes, 50)

   
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
   
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
