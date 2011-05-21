'''
Created on May 18, 2011

@author: Free
'''

import sys, os
import pygame
from pygame.locals import *

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:'
        raise SystemExit, message
    return sound

class Fist(pygame.sprite.Sprite):
    #"""moves a clenched fist on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('fist.bmp', -1)
        self.punching = 0
    
    def update(self):
        #"move the fist based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = pos
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch (self, target):
        #returns true if the fist collides with the target
        if not self.punching:
            self.punching = 1
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)
        
    def unpunch(self):
        #called to pull the fist back
        self.punching = 0

class Chimp(pygame.sprite.Sprite):
    #moves a monkey critter across the screen. It can spin the
    #monkey when it is punched
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('chimp.bmp', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.move = 9
        self.dizzy = 0
        
    def update(self):
        #move the monkey across the screen, and turn at the ends
        newpos = self.rect.move((self.move, 0))
        if not self.area.contains(newpos):
            print "loop"
        if self.rect.left < self.area.left or \
                self.rect.right > self.area.right:
            self.move = -self.move
            newpos = self.rect.move((self.move, 0))
            self.image = pygame.transform.flip(self.image, 1, 0)
        self.rect = newpos
        
    def _spin(self):
        #spin the monkey image
        center = self.rect.center
        self.dizzy += 12
        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            rotate = pygame.transform.rotate
            self.image = rotate(self.original, self.dizzy)
        self.rect = self.image.get_rect(center=center)
    
    def punched(self):
        #this will cause the monkey to start spinning
        if not self.dizzy:
            self.dizzy = 1
            self.original = self.image
        
    