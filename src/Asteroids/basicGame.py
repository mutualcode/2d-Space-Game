#! /usr/bin/env python
# The above line makes this executible in unix systems

import pygame
import random
import math
import os
import sys
import string
pygame.init()

screensize = (640, 480)
playarea = (700, 540)
viewpoint = [350, 270]
forecolor = (255, 255, 255)
backcolor = (0, 0, 0)

Objects = pygame.sprite.Group()
ProtoObjs = pygame.sprite.Group()
ShipGroup = pygame.sprite.GroupSingle()

def get_controls():
    controls = {"left":pygame.K_LEFT, "right":pygame.K_RIGHT, "up":pygame.K_UP, "down":pygame.K_DOWN, "shoot":pygame.K_SPACE, "shield":pygame.K_LCTRL}
    if os.access("controls.txt", os.F_OK) == True:
        controls_file = open("controls.txt", "r")
        for a in ("up", "down", "left", "right", "shoot", "shield"):
            line = controls_file.readline()[:-1]
            if line.isdigit() == True:
                controls[a] = int(line)
        controls_file.close()
    return controls

def save_controls(controls):
    controls_file = open("controls.txt","w")
    for a in ("up", "down", "left", "right", "shoot", "shield"):
        controls_file.write(str(controls[a]) + "\n")
    controls_file.close()

def wrap(num, start, end):
    while num < start:
        num += end - start
    while num > end:
        num -= end - start
    return num

class Obj(pygame.sprite.Sprite):
    angle = 0
    spin = 0
    def __init__(self, pos, speed, groups = []):
        pygame.sprite.Sprite.__init__(self, groups + [Objects])
        self.pos = list(pos)
        self.speed = list(speed)
        self.set_pos_screen()

    def update(self):
        self.angle += self.spin / fps
        self.pos[0] += self.speed[0] / fps
        self.pos[1] += self.speed[1] / fps
        if self.pos[0] > playarea[0]:
            self.pos[0] -= playarea[0]
        elif self.pos[0] < 0:
            self.pos[0] += playarea[0]
        if self.pos[1] > playarea[1]:
            self.pos[1] -= playarea[1]
        elif self.pos[1] < 0:
            self.pos[1] += playarea[1]
        self.set_pos_screen()

    def set_pos_screen(self):
        self.pos_screen = [self.pos[0] - viewpoint[0], self.pos[1] - viewpoint[1]]
        max_radius_x = (playarea[0] - screensize[0]) / 2
        max_radius_y = (playarea[1] - screensize[1]) / 2
        self.pos_screen[0] = wrap(self.pos_screen[0], -max_radius_x, screensize[0] + max_radius_x)
        self.pos_screen[1] = wrap(self.pos_screen[1], -max_radius_y, screensize[1] + max_radius_y)
    def draw(self, surface):
        render_pos = (self.pos_screen[0], self.pos_screen[1])
        dirtyrects = []
        for points_list in self.image_points:
            color = forecolor
            if len(points_list[0]) > 2:
                color = points_list[0]
                points_list = points_list[1:]
            temp_points = []
            for point in points_list:
                temp_points.append((math.sin(point[0] + self.angle) * point[1] + render_pos[0], math.cos(point[0] + self.angle) * point[1] + render_pos[1]))
            pygame.draw.polygon(surface, backcolor, temp_points)
            dirtyrects.append(pygame.draw.aalines(surface, color, 1, temp_points).inflate(2, 2))
        return dirtyrects
class Ship(Obj):
    def __init__(self, pos, speed, radius, movement_keys, groups = []):
        self.radius = radius
        self.movement_keys = movement_keys
        self.normal_points = [[
                (0, radius * 1.3),
                (math.pi / 2, radius / 2),
                (math.pi / 2, radius * 1.2),
                (math.pi * 5 / 6, radius),
                (math.pi * 7 / 6, radius), 
                (math.pi * 3 / 2, radius * 1.2),
                (math.pi * 3 / 2, radius / 2)
            ]]
        self.image_points = self.normal_points
        Obj.__init__(self, pos, speed, groups + [])
        self.collision_type = "Explosive"  

    def control(self, keys):
        self.thrustvolume = 0
        self.spin = 0
        if keys[self.movement_keys["left"]] == 1:
            self.spin += math.pi
        if keys[self.movement_keys["right"]] == 1:
            self.spin -= math.pi
        if keys[self.movement_keys["down"]] == 1:
            self.speed[0] -= math.sin(self.angle) * 400 / 3 / fps
            self.speed[1] -= math.cos(self.angle) * 400 / 3 / fps
        if keys[self.movement_keys["up"]] == 1:
            self.speed[0] += math.sin(self.angle) * 800 / 3 / fps
            self.speed[1] += math.cos(self.angle) * 800 / 3 / fps
def main():
    global viewpoint
    global viewpointspeed
    global score
    global fps
    screen = pygame.display.set_mode(screensize)
    screen.fill(backcolor)
    pygame.display.flip()
    fullscreen = 0
    volume = 100
    clock = pygame.time.Clock()
    controls = get_controls()
    viewpointspeed = [0, 0]
    score = 0
    lives = 0
    respawn_time = 2
    running = 1
    lastbeat = pygame.time.get_ticks()
    beattype = 1
    mode = "playstart"
    olddirtyrects = []
    while running == 1:
        fps = 1000.0 / clock.tick(100)
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = 0          
        
        if mode == "playstart":

                Ship([random.randint(0, playarea[0]), random.randint(0, playarea[0])], [0, 0], 10, controls, groups = [ShipGroup])
                viewpoint = [playarea[0] / 2 - screensize[0] /2, playarea[1] / 2 - screensize[1] /2]
                viewpointspeed = [0, 0]
                score = 0
                lives = 4
                level = 0
                next_life = 10000
                mode = "play"
        if mode == "play":

            if ShipGroup.sprite <> None:
                ship = ShipGroup.sprite
                ship.control(keys)

                rel_x = wrap(viewpoint[0] - ship.pos[0], -playarea[0], 0) + screensize[0] / 2
                rel_y = wrap(viewpoint[1] - ship.pos[1], -playarea[1], 0) + screensize[1] / 2
                px = math.fabs(rel_x / (screensize[0] / 8))
                if px > 1: px = 1.0
                py = math.fabs(rel_y / (screensize[1] / 8))
                if py > 1: py = 1.0
                viewpointspeed[0] -= (viewpointspeed[0] - ship.speed[0]) * (1 - ((1-px)**(1 / fps)))
                viewpointspeed[1] -= (viewpointspeed[1] - ship.speed[1]) * (1 - ((1-py)**(1 / fps)))
                p = (1 - (0.1**(1 / fps)))
                viewpoint[0] += -rel_x * p
                viewpoint[1] += -rel_y * p
                viewpoint[0] = wrap(viewpoint[0], 0, playarea[0])
                viewpoint[1] = wrap(viewpoint[1], 0, playarea[1])

        viewpoint[0] += viewpointspeed[0] / fps
        viewpoint[1] += viewpointspeed[1] / fps
        Objects.update()
        ProtoObjs.update()
        screen.fill((backcolor))
        dirtyrects = []
        for sprite in ProtoObjs.sprites():
            dirtyrects += sprite.draw(screen)
        for sprite in Objects.sprites():
            dirtyrects += sprite.draw(screen)

        pygame.display.update(dirtyrects + olddirtyrects)
        olddirtyrects = dirtyrects
main()
pygame.quit()