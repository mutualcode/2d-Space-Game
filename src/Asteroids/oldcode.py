import sys, os
import pygame
from pygame.locals import *

pygame.init()

class __init__():
    print "cool"

"""size = width, height = 640, 480
speed = [1, 1]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ship = pygame.image.load("ship.png")
shiprect = ship.get_rect()

def shipRotate(degrees):
    
    print "awesome"
    pygame.transform.rotate(ship, degrees)
    # radiansAdjust = degrees * 0.0174532925
    # radians += radiansAdjust;
    

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        
    shiprect = shiprect.move(speed)
    if shiprect.left < 0 or shiprect.right > width:
        speed[0] = -speed[0]
    if shiprect.top < 0 or shiprect.bottom > height:
        speed[1] = -speed[1]
        
    shipRotate(10)
    screen.fill(black)
    screen.blit(ship, shiprect)
    pygame.display.flip()
    """
    
