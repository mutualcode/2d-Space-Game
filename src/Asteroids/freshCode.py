'''
Created on May 20, 2011

@author: Free
'''

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
    controls = {"left":pygame.K_LEFT, "right":pygame.K_RIGHT, "up":pygame.K_UP, "down":pygame.K_DOWN}
    return controls

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
        n[0], -max_radius_x, screensize[0] + max_radius_x)
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
            #pygame.draw.circle(surface, (100, 100, 100), render_pos, self.radius, 1)
        return dirtyrects