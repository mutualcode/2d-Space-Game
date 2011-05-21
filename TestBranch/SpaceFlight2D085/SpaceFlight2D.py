#SpaceFlight2D 0.8.5
#(C) 2008 Robin Wellner
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#Released under GPL (see http://www.gnu.org/licenses/)
#
#Uses:
# * PyPGL by PyMike
# * feedback from PyMike
# * Substitute Clock by Adam Bark
# * toggle_fullscreen() by philhassey & illume + Duoas
# * Bits from Astroids 2 and Planet Vector, both by Ian Mallett
#
#Idea from <http://gpwiki.org/index.php/Game_ideas:_Two-dimensional_Space_Game> by "Saarelma".


###################################
#Importing Etc
try:
    import psyco
    psyco.full()
except:
    pass #error message goes here
import pygame
from pygame.locals import *
import os
from sys import platform as sys_platform
if sys_platform[:3] == 'win':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
from math import *
import random
try: import cPickle
except: import Pickle as cPickle
import ExPGL as PyPGL
import menu
from clock import ABClock
pygame.init()


###################################
#Anti-Aliased Circle
def aacircle(Surface,color,pos,radius,resolution,width=0):
    for I in xrange(resolution):
        pygame.draw.aaline(Surface, color, (pos[0] + radius*cos(2*pi*float(I)/resolution), pos[1] + radius*sin(2*pi*float(I)/resolution)), (pos[0] + radius*cos(2*pi*float(I+1)/resolution), pos[1] + radius*sin(2*pi*float(I+1)/resolution)))


###################################
#Toggle Full Screen
#By philhassey & illume
def toggle_fullscreen():
    screen = pygame.display.get_surface()
    tmp = screen.convert()
    caption = pygame.display.get_caption()
    cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007 

    w,h = screen.get_width(),screen.get_height()
    flags = screen.get_flags()
    bits = screen.get_bitsize()
    
    pygame.display.quit()
    pygame.display.init()
    
    screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
    screen.blit(tmp,(0,0))
    pygame.display.set_caption(*caption)
 
    pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??
 
    pygame.mouse.set_cursor( *cursor )  # Duoas 16-04-2007
    
    return screen


###################################
#Sounds & Graphics
Font = pygame.font.Font("mksanstallx.ttf",14)#("veramono.ttf",10)
BigFont = pygame.font.Font("mksanstallx.ttf",18)#("veramono.ttf",16)

Sounds = {'boom': pygame.mixer.Sound(os.path.join("data", "boom2.ogg")),
          'select': pygame.mixer.Sound(os.path.join("data", "select.ogg")),
          'unselect': pygame.mixer.Sound(os.path.join("data", "unselect.ogg")),
          'shoot': pygame.mixer.Sound(os.path.join("data", "shoot.ogg"))}

try:
    pygame.mixer.music.load(os.path.join("musicdata", "music.ogg"))
    MUSIC_PACK = True
except:
    pygame.mixer.music.load(os.path.join("data", "music1.mid"))
    MUSIC_PACK = False
music = pygame.mixer.music

SoundChannels = {'boom': pygame.mixer.Channel(0),
                 'select': pygame.mixer.Channel(1),
                 'unselect': pygame.mixer.Channel(2),
                 'shoot': pygame.mixer.Channel(3)}

SoundTypes = {'FX': ['boom', 'select', 'unselect', 'shoot']}

vectorImages = {'player/1': PyPGL.image.load(os.path.join("data", 'ship-1.vgf'), (100,100), 0, 0.3),
                'player/2': PyPGL.image.load(os.path.join("data", 'ship-2.vgf'), (0,0), 0, 0.3),
                'player/3': PyPGL.image.load(os.path.join("data", 'ship-3.vgf'), (0,0), 0, 0.3),
                'player/4': PyPGL.image.load(os.path.join("data", 'ship-4.vgf'), (0,0), 0, 0.3),
                'base': PyPGL.image.load(os.path.join("data", 'base.vgf'), (0,0), 0, 0.8),
                'enemy/ship': PyPGL.image.load(os.path.join("data", 'enemy-ship.vgf'), (0,0), 0, 0.5),
                'enemy/base': PyPGL.image.load(os.path.join("data", 'enemy-base.vgf'), (0,0), 0, 0.8)}

PlayerImages = 0
Frames = 0
ArchiveIndex = 0
GamePaused = False
LastGameLoaded = 0
doCheat = False

def Play(sndStr):
    if sndStr != 'music':
        SoundChannels[sndStr].play(Sounds[sndStr], 0)
    else:
        music.play(-1)

def Stop(sndStr):
    if sndStr != 'music':
        SoundChannels[sndStr].stop()
    else:
        music.stop()


###################################
#Introduction Text
IntroText = ("Welcome to SpaceFlight2D...",
             "Use the arrow keys to navigate this introduction.",
             "On a small planet, intelligent beings emerged...",
             "they are your people...",
             "Your people have just discovered space flight technology...",
             "And they are not alone in the universe.",
             "Hold down [UP] to launch your spaceship into space.",
             "Use [LEFT] and [RIGHT] to rotate your ship.",
             "[RIGHTSHIFT] boosts your speed, but "
             "is not very fuel-efficient.",
             "Oil is the main currency of the game.",
             "It can be used to repair ships,",
             "Make buildings, burned as fuel, or shoot enemies.",
             "When landed on a planet, use [B] to build a base.",
             "When landed on a base, use [F] to fill your oil,",
             "[R] to repair your ship "
             "or [D] to drop some of the oil on the planet.",
             "Use [SPACE] to shoot enemy ships and bases.",
             "If you want overview, you can use [Z] to zoom out",
             "and [A] to zoom in.",
             "Press [1], [2], [3] or [4] anytime during the game,",
             "and your game will be saved in the corresponding slot.",
             "This was the introduction. "
             "You will be taken back to the main menu.")


###################################
#Mottos Shown In Main Menu
Mottos = ("Will you succeed in conquering the galaxy?",
          "SpaceFlight2D by Robin Wellner.",
          "Colours are overrated!",
          "Click 'New' to play.",
          "Have you tried the introduction yet?",
          "No comment.",
          "Version 1.0 will be ready some day.",
          "The graphics are just some lines. Well, at least the game's fun.",
          "Have you read all these mottos? I have. I also wrote them.",
          "I'm waiting for you to do something.",
          "Come on then! Get clickin'!",
          "Welcome back!",
          "Don't click [here], nothing will happen.",)


###################################
#Default Settings
MUSIC_VOLUME = 4
FX_VOLUME = 6
KEY_UP = 273
KEY_LEFT = 276
KEY_RIGHT = 275
KEY_FIRE = 32
KEY_LAUNCH = 303
KEY_BUILD = 98
KEY_REPAIR = 114
KEY_FILL = 102
KEY_PAUSE = 112
KEY_ZOOMOUT = 122
KEY_ZOOMIN = 97
KEY_DROP = 100
SCR_FULL = False
SCR_SIZE = (1024,768)

###################################
#Load Settings
f = open(os.path.join('data','settings.txt'))
subj = None
for line in f:
    if line[0] not in '#\n':
        if line[0] == '\t':
            split = line[1:].split()
            if subj == 'Sound Volume':
                if split[0] == 'Music:':
                    MUSIC_VOLUME = int(split[1])
                elif split[0] == 'Effects:':
                    FX_VOLUME = int(split[1])
            elif subj == 'Keys':
                if split[0] == 'Up:':
                    KEY_UP = int(split[1])
                elif split[0] == 'Left:':
                    KEY_LEFT = int(split[1])
                elif split[0] == 'Right:':
                    KEY_RIGHT = int(split[1])
                elif split[0] == 'Fire:':
                    KEY_FIRE = int(split[1])
                elif split[0] == 'Launch:':
                    KEY_LAUNCH = int(split[1])
                elif split[0] == 'Build:':
                    KEY_BUILD = int(split[1])
                elif split[0] == 'Repair:':
                    KEY_REPAIR = int(split[1])
                elif split[0] == 'Fill:':
                    KEY_FILL = int(split[1])
                elif split[0] == 'Pause:':
                    KEY_PAUSE = int(split[1])
                elif split[0] == 'ZoomOut:':
                    KEY_ZOOMOUT = int(split[1])
                elif split[0] == 'ZoomIn:':
                    KEY_ZOOMIN = int(split[1])
                elif split[0] == 'Drop:':
                    KEY_DROP = int(split[1])
            elif subj == 'Screen':
                if split[0] == 'Mode:':
                    SCR_FULL = split[1] == 'Full'
                elif split[0] == 'Size:':
                    SCR_SIZE = tuple(int(i) for i in split[1].split('x'))
        else:
            subj = line[:-1]
f.close()

for Channel in SoundTypes['FX']:
    SoundChannels[Channel].set_volume(FX_VOLUME/10.0)
pygame.mixer.music.set_volume(MUSIC_VOLUME/10.0)

#Warning colours:
CLR_WARNING = (255, 0, 0)
CLR_NORMAL = (255, 255, 255)


###################################
#Defining Classes
class Planet(object):
    def __init__(self, X, Y, Size):
        self.X = X
        self.Y = Y
        self.size = Size
        self.baseAt = None
        self.enemyAt = None
        self.playerLanded = False
        self.oil = Size

class Ship(object):
    def __init__(self, X, Y, Angle, FaceAngle, Speed):
        self.X = X
        self.Y = Y
        self.toX = Speed * -sin(radians(Angle))
        self.toY = Speed * cos(radians(Angle))
        self.angle = Angle
        self.faceAngle = FaceAngle
        self.speed = Speed
        self.oil = 1000
        self.maxoil = 1000
        self.hull = 592
        self.maxhull = 592
    def move(self):
        self.X += self.toX
        self.Y += self.toY

class ownShip(Ship):
    def __init__(self, X, Y, Angle, FaceAngle, Speed):
        Ship.__init__(self, X, Y, Angle, FaceAngle, Speed)
        self.landedOn = None
        self.landedBefore = None
        self.shoot = 0

class enemyShip(Ship):
    def __init__(self, X, Y, Angle, FaceAngle, Speed, Orbit):
        Ship.__init__(self, X, Y, Angle, FaceAngle, Speed)
        self.orbit = Orbit #(centerX, centerY, altitude)
        self.orbitpos = 0
        self.dead = False
        self.explosion = 0
    def move(self):
        diffX = self.X - (self.orbit[0] + self.orbit[2] * cos(radians(self.orbitpos)))
        diffY = self.Y - (self.orbit[1] + self.orbit[2] * sin(radians(self.orbitpos)))
        if abs(diffX)+abs(diffY) < 10:
            self.orbitpos = (self.orbitpos + 2) % 360
        ang = atan2(diffY, diffX)
        diffX = cos(ang)
        diffY = sin(ang)
        self.toX = -diffX * self.speed
        self.toY = -diffY * self.speed
        self.angle = degrees(atan2(-self.toX, self.toY))
        self.faceAngle = self.angle
        Ship.move(self)

class View(object):
    X = 0
    Y = 0
    angle = 0
    zoomfactor = 1

class GameData(object):
    basesBuilt = 0
    homePlanet = None
    tasks = []
    stage = 0
    shootings = 0

class StarData(object):
    params = (random.random(),
              random.random(),
              random.random(),
              random.random(),
              random.random())
    xlist = [-8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8]
    ylist = [-6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6]


###################################
#Creating PlayerShip & Object Containers
playerShip = ownShip(0,0,0,180,0)
playerView = View()
gameData = None #GameData()
starData = StarData()

ShipContainer = []
WreckContainer = []
PlanetContainer = []
ArchiveContainer = []

credits = (("SPACEFLIGHT2D", 0),
           ("(C)2008 Robin Wellner", 15),
           ("CREDITS:", 25),
           ("Astroids 2 by Ian Mallet", 15),
           ("Planet Vector by Ian Mallet", 15),
           ("PyPGL by PyMike", 15),
           ("Substitute Clock by Adam Bark", 15),
           ("toggle_fullscreen()", 15),
           ("by philhassey & illume + Duoas", 15),
           ("FONT:", 25),
           ("Sans Tall X by Manfred Klein", 15),
           ("LICENSES:", 25),
           ("Code: GNU GPL, version 3", 15),
           ("Music: CC-BY-NC-SA", 15),
           ("Font: see TinyUrl.com/mktuo", 15),
           ("IDEA: gpwiki.org", 25))


###################################
#Function For Main Menu
def Menu():
    Clock = ABClock()
    Motto = random.choice(Mottos)
    tick = 0
    focus = 0
    Items = [('New game', 'new'), ('Load game...', 'load'), ('Introduction...', 'intro'), ('Options...', 'options'), ('Exit', 'exit')]
    if gameData is not None:
        Items.insert(1, ('Resume', 'continue'))
    itemheight = 30
    totalheight = 50
    while True:
        Clock.tick(10)
        keystate = pygame.key.get_pressed()
        tick += 1
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return 'exit'
            elif event.type == MOUSEBUTTONDOWN:
                if event.button==1:
                    if 200 < event.pos[0] < 500 and 20 < event.pos[1] < totalheight*len(Items):
                        clicked_item = (event.pos[1] - 20)/totalheight
                        return Items[clicked_item][1]
            elif event.type == MOUSEMOTION:
                if 200 < event.pos[0] < 500 and 20 < event.pos[1] < totalheight*len(Items):
                    focus = (event.pos[1] - 20)/totalheight
            elif event.type == KEYDOWN:
                if event.key in (K_DOWN, K_RIGHT):
                    focus = (focus + 1) % len(Items)
                elif event.key in (K_UP, K_LEFT):
                    focus = (focus - 1) % len(Items)
                elif event.key in (K_RETURN, K_SPACE):
                    return Items[focus][1]
                else:
                    pass
        Surface.fill((0,0,0))
        for n in range(len(Items)):
            draw_item = Items[n][0]
            if focus == n:
                pygame.draw.rect(Surface, (255, 255, 255), (200, 20 + n*totalheight, 300, itemheight))
                Surface.blit(Font.render(draw_item, True, (0, 0, 0)),
                             (215, 25 + n*totalheight))
            else:
                pygame.draw.rect(Surface, (255, 255, 255), (200, 20 + n*totalheight, 300, itemheight), 1)
                Surface.blit(Font.render(draw_item, True, (255, 255, 255)),
                             (215, 25 + n*totalheight))
        #Info text
        if not doCheat:
            Text = Font.render(Motto, True, (255,255,255))
        else:
            Text = Font.render("Cheat mode: ON", True, (255,255,255))
        Surface.blit(Text,(200,310))
        tot_y = 0
        for line, y in credits: #display credits, slowly scrolling upwards, repeating after time
            tot_y += y
            #Surface.blit(Font.render(line, True, (255,255,255)),(10,(tot_y+480-tick*2)%(SCR_SIZE[1]+20)-20))
            Surface.blit(Font.render(line, True, (255,255,255)),(10,tot_y+20))
        pygame.display.flip()


###################################
#Introduction To Game And Game Functions
def Intro():
    Clock = ABClock()
    IntroIndex = 0
    IntroFrames = 0
    Frames = 0
    while True:
        Clock.tick(15)
        keystate = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT:
                return 'exit'
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    Play('unselect')
                    return 'to menu'
                elif event.key == K_LEFT or event.key == K_UP:
                    IntroIndex = IntroIndex-1 if IntroIndex > 0 else 0
                    IntroFrames = 0
                elif event.key == K_RIGHT or event.key == K_DOWN:
                    IntroIndex += 1
                    if IntroIndex >= len(IntroText):
                        Play('unselect')
                        return 'to menu'
                    IntroFrames = 0
        IntroFrames += 1
        Frames+=1
        if IntroFrames > 50:
            IntroIndex += 1
            if IntroIndex >= len(IntroText):
                Play('unselect')
                return 'to menu'
            IntroFrames = 0
        Surface.fill((0,0,0))
        if IntroIndex < len(IntroText)-1:
            DrawnText = BigFont.render(IntroText[IntroIndex+1], True, (55,55,55))
            Surface.blit(DrawnText,(50, 90 - IntroFrames))
        if IntroFrames < 10:
            Color = 55 + IntroFrames * 20
            if IntroIndex > 0:
                Color2 = 255 - IntroFrames * 25.5
                DrawnText = BigFont.render(IntroText[IntroIndex-1], True, (Color2,Color2,Color2))
                Surface.blit(DrawnText,(100, 40))
        else:
            Color = 255
        DrawnText = BigFont.render(IntroText[IntroIndex], True, (Color,Color,Color))
        Surface.blit(DrawnText,(50 + IntroFrames, 40))
        pygame.display.flip()


###################################
#Function For Options Menu
def Options():
    global FX_VOLUME, MUSIC_VOLUME, SCR_FULL, Surface
    f = 0
    while True:
        Items = [('Sound effects volume', 'fx', 'slider', (FX_VOLUME, 0, 10)),
                 ('Music volume', 'music', 'slider', (MUSIC_VOLUME, 0, 10)),
                 ('Full screen', 'full', 'checkbox', SCR_FULL),
                 ('Keys', 'keys', 'button'),
                 ('The Old Options menu', 'old', 'button'),
                 ('Apply', 'ok', 'button'),
                 ('Back', 'cancel', 'cancelbutton'),
                ]
        result, data = menu.menu(Surface, Items, 30, 200, 30, 30, 50, 300, Font, f)
        if result == 'exit':
            return 'exit'
        elif result == 'cancel':
            return 'to menu'
        elif result == 'ok':
            FX_VOLUME = data['fx'].index
            MUSIC_VOLUME = data['music'].index
            for Channel in SoundTypes['FX']:
                SoundChannels[Channel].set_volume(FX_VOLUME/10.0)
            pygame.mixer.music.set_volume(MUSIC_VOLUME/10.0)
            if data['full'].checked != SCR_FULL:
                Surface = toggle_fullscreen()
                SCR_FULL = not SCR_FULL
            f = 5
        elif result == 'old':
            OldOptions()
            f = 4
        elif result == 'keys':
            ChangeKeys()
            f = 3


###################################
#Menu For Changing Game Keys
def ChangeKeys():
    f = 0
    keylist = [('Speed up', 'KEY_UP'),
               ('Steer left', 'KEY_LEFT'),
               ('Steer right', 'KEY_RIGHT'),
               ('Fire lasers', 'KEY_FIRE'),
               ('Launch', 'KEY_LAUNCH'),
               ('Build base', 'KEY_BUILD'),
               ('Repair ship', 'KEY_REPAIR'),
               ('Fill tank', 'KEY_FILL'),
               ('Pause game', 'KEY_PAUSE'),
               ('Zoom in', 'KEY_ZOOMIN'),
               ('Zoom out', 'KEY_ZOOMOUT'),
               ('Drop oil', 'KEY_DROP'),
              ]
    g = globals()
    while True:
        Items = []
        for i in keylist:
            Items.append((i[0] + ' (' + ReprKey(g[i[1]])+ ')', i[1], 'button'))
        Items.append(('Back', 'cancel', 'cancelbutton'))
        result, data = menu.menu(Surface, Items, 30, 200, 30, 30, 50, 300, Font, f)
        if result.startswith('KEY'):
            ChangeKey(result)
            for i in range(len(Items)):
                if Items[i][1] == result:
                    f=i
        else:
            break


###################################
#Change A Game Key
def ChangeKey(keyname):
    key = globals()[keyname]
    name = keyname[4:].capitalize()
    Clock = ABClock()
    while True:
        Clock.tick(40)
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key in (K_ESCAPE, K_RETURN):
                    return
                elif event.key not in (K_s, K_F1, K_F2, K_F3, K_F4):
                    globals()[keyname] = event.key
                    return
        Surface.fill((0,0,0))
        Text = Font.render('Press a new key for the action '+name+'.', True, (255,255,255))
        Surface.blit(Text,(20,20))
        Text = Font.render('Current key: '+ReprKey(key)+'.', True, (255,255,255))
        Surface.blit(Text,(20,50))
        pygame.display.flip()


###################################
#Representation Of Key
def ReprKey(key):
    #keydict = {getattr(pygame.locals, i): i[2:].capitalize() for i in dir(pygame.locals) if i.startswith('K_')} #no Python3.0
    keydict = dict((getattr(pygame.locals, i), i[2:].capitalize()) for i in dir(pygame.locals) if i.startswith('K_'))
    return keydict.get(key, 'Unknown key')

###################################
#Old Function For Options Menu
def OldOptions():
    global FX_VOLUME, MUSIC_VOLUME
    Clock = ABClock()
    while True:
        Clock.tick(10)
        keystate = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == QUIT:
                return 'exit'
            elif keystate[K_ESCAPE]:
                Play('unselect')
                return 'to menu'
            elif event.type == MOUSEBUTTONDOWN:
                if event.button==1:
                    if 145 < event.pos[0] < 235:
                        if 10 < event.pos[1] < 30:
                            Play('unselect')
                            return 'to menu'
                    if 140 < event.pos[0] < 240:
                        if 60 < event.pos[1] < 75:
                            FX_VOLUME = round((event.pos[0] - 140) / 10.0)
                            for Channel in SoundTypes['FX']:
                                SoundChannels[Channel].set_volume(FX_VOLUME/10.0)
                            Play('select')
                        elif 80 < event.pos[1] < 95:
                            MUSIC_VOLUME = round((event.pos[0] - 140) / 10.0)
                            pygame.mixer.music.set_volume(MUSIC_VOLUME/10.0)
                            Play('select')
        Surface.fill((0,0,0))
        Text = Font.render("Options", True, (255,255,255))
        Surface.blit(Text,(20,15))
        Text = Font.render("Volume:", True, (255,255,255))
        Surface.blit(Text,(35,40))
        Text = Font.render("Sound Effects", True, (255,255,255))
        Surface.blit(Text,(40,60))
        Text = Font.render("Music", True, (255,255,255))
        Surface.blit(Text,(40,80))
        Text = Font.render("Keys:", True, (255,255,255))
        Surface.blit(Text,(35,110))
        Text = Font.render("Default", True, (155,155,155))
        Surface.blit(Text,(80,110))
        Text = Font.render("See data/settings.txt", True, (255,255,255))
        Surface.blit(Text,(40,130))
        Text = Font.render("Back to menu", True, (255,255,255))
        Surface.blit(Text,(150,10))
        pygame.draw.rect(Surface, (255, 255, 255), (145, 10, 90, 20), 1)
        pygame.draw.rect(Surface, (155, 155, 155), (140, 60, 100, 15))
        pygame.draw.rect(Surface, (155, 155, 155), (140, 80, 100, 15))
        if FX_VOLUME:
            pygame.draw.rect(Surface, (255, 255, 255), (140, 60, FX_VOLUME*10, 15))
        if MUSIC_VOLUME:
            pygame.draw.rect(Surface, (255, 255, 255), (140, 80, MUSIC_VOLUME*10, 15))
        pygame.display.flip()


###################################
#Get Input During Game
def GetInput():
    keystate = pygame.key.get_pressed()
    global PlayerImages, GamePaused, LastGameLoaded, doCheat
    PlayerImages = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            return 'exit'
        elif event.type == KEYUP:
            if event.key == KEY_PAUSE:
                GamePaused = not GamePaused
    if keystate[K_ESCAPE]:
        ##FadeOut('music')
        return 'to menu'
    if not GamePaused:
        if keystate[KEY_UP]:
            playerShip.toX -= sin(radians(playerShip.faceAngle)) * .1
            playerShip.toY += cos(radians(playerShip.faceAngle)) * .1
            playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
            playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
            playerShip.oil -= 0.1
            PlayerImages = 1
        if keystate[KEY_LEFT]:
            playerShip.faceAngle -= 3
            playerShip.faceAngle = playerShip.faceAngle % 360
        if keystate[KEY_RIGHT]:
            playerShip.faceAngle += 3
            playerShip.faceAngle = playerShip.faceAngle % 360
        if keystate[KEY_FIRE]:
            playerShip.oil -= 0.1
            Hit = False
            playerShip.shoot = 3
            for item in ShipContainer:
                if ((playerShip.X - item.X)**2 + (playerShip.Y + item.Y)**2)**.5 < 200:
                    item.hull -= 10
                    Hit = True
                    if item.hull <= 0:
                        Play('boom')
                        item.dead = True
                        item.explosion = 0
                        WreckContainer.append(ShipContainer.pop(ShipContainer.index(item)))
                        #del item
            for item in PlanetContainer:
                    if item.enemyAt is not None:
                        X = item.X + item.size*cos(radians(item.enemyAt+90))
                        Y = item.Y + item.size*sin(radians(item.enemyAt+90))
                        if ((playerShip.X - X)**2 + (playerShip.Y + Y)**2)**.5 < 200:
                            Play('boom')
                            item.enemyAt = None
            if Hit: Play('shoot')
        if keystate[KEY_LAUNCH]:
            PlayerImages = 2
            playerShip.toX -= sin(radians(playerShip.faceAngle)) * 2
            playerShip.toY += cos(radians(playerShip.faceAngle)) * 2
            playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
            playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
            playerShip.oil -= 10
        if keystate[KEY_BUILD]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].baseAt == None and PlanetContainer[playerShip.landedOn].enemyAt == None:
                    if PlanetContainer[playerShip.landedOn].oil >= 200:
                        PlanetContainer[playerShip.landedOn].oil -= 200
                        XDiff = playerShip.X - PlanetContainer[playerShip.landedOn].X
                        YDiff = playerShip.Y + PlanetContainer[playerShip.landedOn].Y
                        PlanetContainer[playerShip.landedOn].baseAt = degrees(atan2(-XDiff, -YDiff))
                        PlanetContainer[playerShip.landedOn].playerLanded = 'base'
                        gameData.basesBuilt += 1
                        checkProgress('base built')
        if keystate[KEY_REPAIR]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
                    if PlanetContainer[playerShip.landedOn].oil >= playerShip.maxhull - playerShip.hull:
                        PlanetContainer[playerShip.landedOn].oil -= playerShip.maxhull - playerShip.hull
                        playerShip.hull = playerShip.maxhull
                    else:
                        playerShip.hull += PlanetContainer[playerShip.landedOn].oil
                        PlanetContainer[playerShip.landedOn].oil = 0
        if keystate[KEY_FILL]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
                    if PlanetContainer[playerShip.landedOn].oil >= playerShip.maxoil - playerShip.oil:
                        PlanetContainer[playerShip.landedOn].oil -= playerShip.maxoil - playerShip.oil
                        playerShip.oil = playerShip.maxoil
                    else:
                        playerShip.oil += PlanetContainer[playerShip.landedOn].oil
                        PlanetContainer[playerShip.landedOn].oil = 0
        if keystate[KEY_DROP]:
            if playerShip.landedOn is not None:
                if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
                    if playerShip.oil > 20:
                        playerShip.oil -= 5
                        PlanetContainer[playerShip.landedOn].oil += 5
    if keystate[K_s]:
        SaveAs()
    if keystate[K_g] and doCheat == False:
        doCheat = 1
    if keystate[K_v] and doCheat == 1:
        doCheat = 2
    if keystate[K_x] and doCheat == 2:
        doCheat = 3
    if doCheat == 3:
############################################TESTING ONLY##########
        if keystate[K_F1]:                                 #######
            playerShip.toX = 0                             #######
            playerShip.toY = 0                             #######
        elif keystate[K_F2]:                               #######
            playerShip.hull = playerShip.maxhull           #######
            playerShip.oil = playerShip.maxoil             #######
        elif keystate[K_F3]:                               #######
            playerShip.toX *= 1.01                         #######
            playerShip.toY *= 1.01                         #######
        elif keystate[K_F4]:                               #######
            if gameData.stage == 0:                        #######
                gameData.stage = 1                         #######
                gameData.tasks.append("Fly to Sector 0:0") #######
##################################################################
    if keystate[KEY_ZOOMIN]:
        if playerView.zoomfactor > 1:
            playerView.zoomfactor = playerView.zoomfactor * .9
    elif keystate[KEY_ZOOMOUT]:
        if playerView.zoomfactor < 100:
            playerView.zoomfactor = playerView.zoomfactor / .9


###################################
#Check Progress & Continue Story Line
def checkProgress(action):
    if action == 'base built':
        if (gameData.basesBuilt % 9) == 8:
            if gameData.basesBuilt == 26:
                DisplayMessage("Our radio found a strange signal. It's came from really far.", 'Misson Control')
                gameData.tasks.append("Fly to Sector 0:0")
                gameData.stage = 1
                DisplayMessage("Return to our home planet, where we'll equip you with the means to go there.", 'Misson Control')
            else:
                DisplayMessage("You have built "+str(gameData.basesBuilt)+" bases now. Congratulations!")
                rndX = random.choice((-1, 1)) * random.randint(3, 10) * 10000
                rndY = random.choice((-1, 1)) * random.randint(3, 10) * 10000
                for newPlanetX in range(-1, 2):
                    for newPlanetY in range(-1, 2):
                        ArchiveContainer.append(Planet(rndX + newPlanetX * 20000 + random.randint(-8000, 8000), rndY + newPlanetY * 18000 + random.randint(-6000, 6000), random.randint(250, 1500)))
                        ArchiveContainer[-1].enemyAt = random.choice((None, random.randint(0, 360)))
                DisplayMessage("A new system is found in Sector "+ str(int(floor(rndX/30000))) + ":" + str(int(floor(-rndY/30000)))+ ". Fly to it to build some bases on it.", 'Misson Control')
                gameData.tasks.append("Fly to Sector "+ str(int(floor(rndX/30000))) + ":" + str(int(floor(-rndY/30000))))
            try:
                gameData.tasks.remove("Conquer this system")
            except:
                pass
        elif gameData.basesBuilt == 1:
            DisplayMessage("You have built a base now. Good! Now build bases on the other planets.", 'Misson Control')
            gameData.tasks.remove("Build a base on another planet")
            gameData.tasks.append("Conquer this system")
        elif gameData.stage == 2:
            gameData.tasks.remove("Build a base on that planet")
            DisplayMessage("That was a stupid move of you.", "The other spaceship")
            DisplayMessage("Just stay away from our main planet. I'll give you the coordinates, so you can avoid it.", "The other spaceship")
            rndX = random.choice((-1, 1)) * 140000
            rndY = random.choice((-1, 1)) * 140000
            pX = rndX + random.randint(-3000, 3000)
            pY = rndY + random.randint(-3000, 3000)
            ArchiveContainer.append(Planet(pX, pY, 2000))
            ArchiveContainer[-1].enemyAt = random.randint(0, 360)
            for n in range(1, 10):
                o = random.randint(0, 360)
                bound = 2000+n*400
                ArchiveContainer.append(enemyShip(pX + bound*cos(radians(o)), pY + bound*sin(radians(o)), 0, 0, 2+4.0/n ,(pX,pY,bound)))
                ArchiveContainer[-1].orbitpos = o
            DisplayMessage("You got what from who? Well, I think you should go there anyway.", 'Misson Control')
            gameData.tasks.append("Fly to Sector "+ str(int(floor(rndX/30000))) + ":" + str(int(floor(-rndY/30000))))
            gameData.stage = 3
    elif action == 'sector changed':
        try:
            gameData.tasks.remove("Fly to Sector " + str(int(floor(playerShip.X/30000))) + ":" + str(int(floor(playerShip.Y/30000))))
            if gameData.stage == 0:
                gameData.tasks.append("Conquer this system")
            elif gameData.stage == 1:
                DisplayMessage("Good. You'll get a better hull and a larger oilsupply. You only have to fill it yourself.", 'Misson Control')
                playerShip.maxoil = 3000
                playerShip.maxhull = 1200
                DisplayMessage("If you think you're ready, just go to the sector on your task list.", 'Misson Control')
                rndX = random.choice((-1, 1)) * random.randint(11, 12) * 10000
                rndY = random.choice((-1, 1)) * random.randint(11, 12) * 10000
                pX = rndX + random.randint(-3000, 3000)
                pY = rndY + random.randint(-3000, 3000)
                ArchiveContainer.append(Planet(pX, pY, 1700))
                ArchiveContainer[-1].enemyAt = random.randint(0, 360)
                ArchiveContainer.append(enemyShip(pX + 2000, pY, 0, 0, 5 ,(pX,pY,2000)))
                gameData.tasks.append("Fly to Sector "+ str(int(floor(rndX/30000))) + ":" + str(int(floor(-rndY/30000))))
                gameData.stage = 2
            elif gameData.stage == 2:
                DisplayMessage("Who are you, and what are you doing here?", "Unknown source")
                DisplayMessage("This is our planet. Get away before we attack you.", "The same unknown source")
                DisplayMessage("What are you waiting for? Go investigate that planet!", "Mission Control")
                gameData.tasks.append("Build a base on that planet")
        except:
            pass


###################################
#Move Ships & Collision Detection
def Move():
    global ArchiveIndex, gameData
    playerShip.landedBefore = playerShip.landedOn
    playerShip.landedOn = None
    for Thing in PlanetContainer:
        XDiff = playerShip.X - Thing.X
        YDiff = playerShip.Y + Thing.Y
        Distance = (XDiff**2+YDiff**2)**0.5
        if Distance > 40000:
           ArchiveContainer.append(Thing)
           PlanetContainer.remove(Thing)
        elif Distance <= Thing.size+26:
            #collision OR landed --> check speed
            if playerShip.speed > 2:
                playerShip.hull -= playerShip.speed**2 #-> 25 ppf will kill you
            if playerShip.hull <= 0:
                #crash!
                #print 'Crash!'
                Play('boom')
                if gameData.homePlanet in ArchiveContainer:
                    PlanetContainer.append(gameData.homePlanet)
                    ArchiveContainer.remove(gameData.homePlanet)
                if gameData.homePlanet.oil > 1592: #592+1000
                    playerShip.hull = 592
                    playerShip.oil = 1000
                    playerShip.X = 0
                    playerShip.Y = 25
                    playerShip.toX = 0
                    playerShip.toY = 0
                    playerShip.faceAngle = 180
                    gameData.homePlanet.oil -= 1592
                else:
                    playerShip.hull = 0
                    DisplayMessage('You crashed and died in the explosion. You lose.')
                    gameData = None
                    return 'to menu'
            else:
                #land!
                playerShip.landedOn = PlanetContainer.index(Thing)
                if not Thing.playerLanded:
                    if Thing.baseAt is not None and \
                       ((Thing.X+Thing.size*cos(radians(Thing.baseAt+90)) - playerShip.X)**2 + (-Thing.Y-Thing.size*sin(radians(Thing.baseAt+90)) - playerShip.Y)**2)**.5 < 60:
                        Thing.playerLanded = 'base'
                    else:
                        Thing.playerLanded = True
                    playerShip.toX = 0
                    playerShip.toY = 0
                    continue
                else:
                    NDistance = ((playerShip.X+playerShip.toX-Thing.X)**2 +
                                 (playerShip.Y+playerShip.toY+Thing.Y)**2)**0.5
                    if NDistance < Distance:
                        playerShip.toX = Thing.size/20/Distance * XDiff/Distance
                        playerShip.toY = Thing.size/20/Distance * YDiff/Distance
                        playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
                        playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
                        playerShip.move()
                        playerShip.toX = 0
                        playerShip.toY = 0
                        continue
        else:
            Thing.playerLanded = False
        if gameData.stage > 0 and Thing.enemyAt is not None:
            X = Thing.X + Thing.size*cos(radians(Thing.enemyAt+90))
            Y = Thing.Y + Thing.size*sin(radians(Thing.enemyAt+90))
            if ((playerShip.X - X)**2 + (playerShip.Y + Y)**2)**.5 < 300:
                playerShip.hull -= random.randint(1,3)*random.randint(1,3)
                gameData.shootings = 3
                if playerShip.hull <= 0:
                    Play('boom')
                    if gameData.homePlanet in ArchiveContainer:
                        PlanetContainer.append(gameData.homePlanet)
                        ArchiveContainer.remove(gameData.homePlanet)
                    if gameData.homePlanet.oil > 1592: #592+1000
                        playerShip.hull = 592
                        playerShip.oil = 1000
                        playerShip.X = 0
                        playerShip.Y = 25
                        playerShip.toX = 0
                        playerShip.toY = 0
                        playerShip.faceAngle = 180
                        gameData.homePlanet.oil -= 1592
                    else:
                        ##FadeOut('music')
                        playerShip.hull = 0
                        DisplayMessage('You where shot and died. You lose.')
                        gameData = None
                        return 'to menu'
        #print Thing.playerLanded
        #F = (G*M*M)/(R**2)
        Acceleration = Thing.size/20/Distance #0.125*(P.mass*P2.mass)/(Distance**2)
        #F = M*A  ->  A = F/M
        playerShip.toX -= Acceleration * XDiff/Distance
        playerShip.toY -= Acceleration * YDiff/Distance
        playerShip.speed = (playerShip.toX**2 + playerShip.toY**2) ** 0.5
        playerShip.angle = degrees(atan2(-playerShip.toX, playerShip.toY))
    for Thing in ShipContainer:
        #move ships
        Thing.move()
        if gameData.stage > 0:
            if ((playerShip.X - Thing.X)**2 + (playerShip.Y + Thing.Y)**2)**.5 < 300:
                playerShip.hull -= random.randint(1,3)*random.randint(1,3)
                gameData.shootings = 3
                if playerShip.hull <= 0:
                    Play('boom')
                    if gameData.homePlanet in ArchiveContainer:
                        PlanetContainer.append(gameData.homePlanet)
                        ArchiveContainer.remove(gameData.homePlanet)
                    if gameData.homePlanet.oil > 1592: #592+1000
                        playerShip.hull = 592
                        playerShip.oil = 1000
                        playerShip.X = 0
                        playerShip.Y = 25
                        playerShip.toX = 0
                        playerShip.toY = 0
                        playerShip.faceAngle = 180
                        gameData.homePlanet.oil -= 1592
                    else:
                        playerShip.hull = 0
                        DisplayMessage('You where shot and died. You lose.')
                        gameData = None
                        return 'to menu'
    for Thing in WreckContainer:
        Thing.explosion += 0.1
        if Thing.explosion > 10:
            WreckContainer.remove(Thing)
    playerShip.move()
    if floor(playerShip.X/30000) != floor((playerShip.X-playerShip.toX)/30000) or floor(playerShip.Y/30000) != floor((playerShip.Y-playerShip.toY)/30000):
        checkProgress('sector changed')
    playerView.X = playerShip.X #+ View.X * 9) // 10
    playerView.Y = playerShip.Y #+ View.Y * 9) // 10
    if playerShip.oil <= 0:
        Play('boom')
        if gameData.homePlanet in ArchiveContainer:
            PlanetContainer.append(gameData.homePlanet)
            ArchiveContainer.remove(gameData.homePlanet)
        if gameData.homePlanet.oil > 1592: #592+1000
            playerShip.hull = 592
            playerShip.oil = 1000
            playerShip.X = 0
            playerShip.Y = 25
            playerShip.toX = 0
            playerShip.toY = 0
            playerShip.faceAngle = 180
            gameData.homePlanet.oil -= 1592
        else:
            playerShip.oil = 0
            DisplayMessage("Your oilsupply is empty. You can't do anything anymore. You lose.")
            gameData = None
            return 'to menu'
        playerShip.X = 0
        playerShip.Y = 25
        playerShip.toX = 0
        playerShip.toY = 0
        playerShip.faceAngle = 180
        playerShip.oil = 1000
    if Frames % 10 == 0:
        try:
            Distance = ((playerShip.X - ArchiveContainer[ArchiveIndex].X)**2+(playerShip.Y + ArchiveContainer[ArchiveIndex].Y)**2)**0.5
            if Distance < 35000:
                T = ArchiveContainer.pop(ArchiveIndex)
                if type(T) == Planet:
                    PlanetContainer.append(T)
                elif T.dead:
                    WreckContainer.append(T)
                else:
                    ShipContainer.append(T)
                ArchiveIndex = ArchiveIndex % len(ArchiveContainer)
            else:
                ArchiveIndex = (ArchiveIndex + 1) % len(ArchiveContainer)
        except: #If the ArchiveContainer is empty
            pass


###################################
#Function To Draw Everything
def Draw(update=True):
    global WreckContainer, ShipContainer, PlanetContainer, Frames, GamePaused, ZoomedOut
    if gameData.shootings > 0:
        Surface.fill((100,0,0))
        gameData.shootings -= 1
    else:
        Surface.fill((0,0,0))
    #Display direction (Thanks, retroredge, for pointing it out!)
    tmpColor = (playerView.zoomfactor*2,)*3
    aacircle(Surface, tmpColor, (320, 240), 180, 45, 1)
    rads = radians(playerShip.faceAngle+90)
    rads2 = rads + 2.094 #radians(120)
    rads3 = rads - 2.094 #this should be precise enough
    xy = (320+180*cos(rads),240+180*sin(rads))
    pygame.draw.aaline(Surface, tmpColor, xy, (320+180*cos(rads2),240+180*sin(rads2)), 1)
    pygame.draw.aaline(Surface, tmpColor, xy, (320+180*cos(rads3),240+180*sin(rads3)), 1)
    if playerShip.shoot > 0:
        pygame.draw.circle(Surface,(128,128,128),(320, 240), int(200/playerView.zoomfactor))
        playerShip.shoot -= 1

    STARy = 240 - playerView.Y/200
    STARx = 320 - playerView.X/200
    for i in starData.xlist:
        for j in starData.ylist:
            tmp = (i+starData.params[0])*starData.params[1]+(j+starData.params[2])*starData.params[3]+starData.params[4]
            #Surface.set_at((int(STARx + i * 100 * cos(tmp)), int(STARy + j * 100 * sin(tmp))), (255,255,255))
            x = STARx + i * 200 * cos(tmp)
            y = STARy + j * 200 * sin(tmp)
            pygame.draw.aaline(Surface, (255,255,255), (x,y), (x+1.5,y+1.5), 1)
            pygame.draw.aaline(Surface, (255,255,255), (x+1.5,y), (x,y+1.5), 1)
    
    for Thing in PlanetContainer:
        aacircle(Surface,(255,255,255),((Thing.X-playerView.X)/playerView.zoomfactor+320,(-Thing.Y-playerView.Y)/playerView.zoomfactor+240),Thing.size/playerView.zoomfactor,int(10*log(Thing.size*.2/playerView.zoomfactor,2))+20,1)
        if Thing.baseAt is not None:
            vectorImages['base'].position((320+(-playerView.X+Thing.X+Thing.size*cos(radians(Thing.baseAt+90)))/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y-Thing.size*sin(radians(Thing.baseAt+90)))/playerView.zoomfactor))
            vectorImages['base'].rotate(Thing.baseAt)
            vectorImages['base'].scale(0.8/playerView.zoomfactor)
            vectorImages['base'].draw(Surface, (255,255,255))
        if Thing.enemyAt is not None:
            vectorImages['enemy/base'].position((320+(-playerView.X+Thing.X+Thing.size*cos(radians(Thing.enemyAt+90)))/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y-Thing.size*sin(radians(Thing.enemyAt+90)))/playerView.zoomfactor))
            vectorImages['enemy/base'].rotate(Thing.enemyAt)
            vectorImages['enemy/base'].scale(0.8/playerView.zoomfactor)
            vectorImages['enemy/base'].draw(Surface, (255,255,255))
    for Thing in ShipContainer:
        vectorImages['enemy/ship'].position((320+(-playerView.X+Thing.X)/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y)/playerView.zoomfactor))
        vectorImages['enemy/ship'].rotate(Thing.faceAngle)
        vectorImages['enemy/ship'].scale(0.5/playerView.zoomfactor)
        vectorImages['enemy/ship'].explode(0)
        vectorImages['enemy/ship'].draw(Surface, (255,255,255))
        #De-comment this to see where enemy ships are flying to
        #vectorImages['enemy/ship'].position((320+(-playerView.X+Thing.orbit[0] + Thing.orbit[2]*cos(radians(Thing.orbitpos)))/playerView.zoomfactor ,240+(-playerView.Y-Thing.orbit[1] - Thing.orbit[2]*sin(radians(Thing.orbitpos)))/playerView.zoomfactor))
        #vectorImages['enemy/ship'].rotate(Thing.faceAngle)
        #vectorImages['enemy/ship'].scale(0.5/playerView.zoomfactor)
        #vectorImages['enemy/ship'].draw(Surface, (50,50,50))
    for Thing in WreckContainer:
        vectorImages['enemy/ship'].position((320+(-playerView.X+Thing.X)/playerView.zoomfactor ,240+(-playerView.Y-Thing.Y)/playerView.zoomfactor))
        vectorImages['enemy/ship'].rotate(Thing.faceAngle)
        vectorImages['enemy/ship'].scale(0.5/playerView.zoomfactor)
        vectorImages['enemy/ship'].explode(Thing.explosion)
        vectorImages['enemy/ship'].draw(Surface, (255,255,255), max=int(7-Thing.explosion))

    if PlayerImages == 0:
        imgStr = '1'
    elif PlayerImages == 1:
        if (Frames//5) % 2:
            imgStr = '3'
        else:
            imgStr = '2'
    elif PlayerImages == 2:
        if (Frames//5) % 2:
            imgStr = '2'
        else:
            imgStr = '4'
    vectorImages['player/'+imgStr].position((320, 240))##((320+playerShip.X-playerView.X,240+playerShip.Y-playerView.Y))
    vectorImages['player/'+imgStr].rotate(-playerShip.faceAngle-180+playerView.angle)
    vectorImages['player/'+imgStr].scale(0.3/playerView.zoomfactor)
    vectorImages['player/'+imgStr].draw(Surface, (255,255,255))
    
    pygame.draw.rect(Surface, (255-playerShip.oil*255/playerShip.maxoil if playerShip.oil > 0 else 255, 0, playerShip.oil*255/playerShip.maxoil if playerShip.oil > 0 else 0), (8, 8+(playerShip.maxoil-playerShip.oil)*464/playerShip.maxoil, 20, playerShip.oil*464/playerShip.maxoil), 0)
    if playerShip.oil < 100:
        c_ = CLR_WARNING
        n_ = 2
    else:
        c_ = CLR_NORMAL
        n_ = 1
    pygame.draw.rect(Surface, c_, (8, 8, 20, 464), n_)

    pygame.draw.rect(Surface, (0, 255, 0), (40, 8, 592*playerShip.hull/playerShip.maxhull, 20), 0)
    if playerShip.hull < 50:
        c_ = CLR_WARNING
        n_ = 2
    else:
        c_ = CLR_NORMAL
        n_ = 1
    pygame.draw.rect(Surface, c_, (40, 8, 592, 20), n_)
    
    if playerShip.speed > 16:
        c_ = CLR_WARNING
    else:
        c_ = CLR_NORMAL
    Text = BigFont.render("Speed: %.2d p/f" % playerShip.speed, True, c_)
    Surface.blit(Text,(40,40))
    if GamePaused:
        Text = Font.render("Game paused...", True, (255,255,255))
        Surface.blit(Text,(40,80))
    Text = Font.render("Bases built: " + str(gameData.basesBuilt), True, (255,255,255))
    Surface.blit(Text,(40,95))
    Text = Font.render("You are in Sector " + str(int(floor(playerShip.X/30000))) + ":" + str(int(floor(playerShip.Y/30000))), True, (255,255,255))
    Surface.blit(Text,(40,125))
    top = 40
    for task in gameData.tasks:
        Text = Font.render(task, True, (255,255,255))
        top += 13
        Surface.blit(Text,(400,top))
    if playerShip.landedOn is not None:
        if PlanetContainer[playerShip.landedOn].playerLanded == 'base':
            Text = Font.render("Oil on planet: " + str(int(PlanetContainer[playerShip.landedOn].oil)), True, (255,255,255))
            Surface.blit(Text,(40,110))
    elif playerShip.landedBefore is not None:
        if PlanetContainer[playerShip.landedBefore].playerLanded == 'base':
            Text = Font.render("Oil on planet: " + str(int(PlanetContainer[playerShip.landedBefore].oil)), True, (255,255,255))
            Surface.blit(Text,(40,110))
    if update:
        pygame.display.flip()


###################################
#Displaying an ingame message
def DisplayMessage(msg, source='Game'):
    global GamePaused
    GamePaused = True
    Clock = ABClock()
    while True:
        Clock.tick(10)
        for event in pygame.event.get():
            if event.type == QUIT:
                GamePaused = False
                return
        keystate = pygame.key.get_pressed()
        if keystate[K_RETURN]:
            GamePaused = False
            return
        Draw(False)
        if Font.size(msg)[0] > 380:
            words = msg.split(' ')
            print_text = []
            line = ''
            height = 0
            for word in words:
                if Font.size(line + word + " ")[0] < 380:
                    line += word + ' '
                else:
                    print_text.append(line)
                    height += Font.size(line)[1]
                    line = word + " "
            print_text.append(line)
            height += Font.size(line)[1]
        else:
            print_text = [msg]
            height = Font.size(msg)[1]
        pygame.draw.rect(Surface, (155, 155, 155), (100, 160, 400, 40), 0)
        pygame.draw.rect(Surface, (255, 255, 255), (100, 200, 400, 40+height), 0)
        Text = Font.render(source, True, (0,0,0))
        Surface.blit(Text,(110,170))
        for i in range(len(print_text)):
            m = print_text[i]
            Text = Font.render(m, True, (0,0,0))
            Surface.blit(Text,(110,210+i*height/len(print_text)))
        Text = Font.render("Press [RETURN] to continue...", True, (0,0,0))
        Surface.blit(Text,(220,220+height))
        pygame.display.flip()


###################################
#Starting A New Game
def SetUpGame():
    global WreckContainer, ShipContainer, PlanetContainer, ArchiveContainer, playerShip, gameData
    gameData = GameData()
    PlanetContainer = [Planet(0, -1050, 1000)]
    gameData.homePlanet = PlanetContainer[0]
    gameData.tasks = ["Build a base on another planet"]
    PlanetContainer[0].baseAt = 0
    ShipContainer = []
    ShipContainer.append(enemyShip(200, 200, 0, 0, 2, (0, -1050, 1500)))
    WreckContainer = []
    for newPlanetX in range(-1, 2):
        for newPlanetY in range(-1, 2):
            if newPlanetX == 0 and newPlanetY == 0: continue
            PlanetContainer.append(Planet(newPlanetX * 20000 + random.randint(-8000, 8000), newPlanetY * 18000 + random.randint(-6000, 6000), random.randint(250, 1500)))
            PlanetContainer[-1].enemyAt = random.choice((None, random.randint(0, 360)))
    PlanetContainer[0].playerLanded = 'base'
    ArchiveContainer = []
    playerShip.X = 0
    playerShip.Y = 25
    playerShip.angle = 0
    playerShip.faceAngle = 180
    playerShip.speed = 0
    playerShip.hull = 592
    playerShip.toX = 0
    playerShip.toY = 0
    playerView.X = 0
    playerView.Y = 0
    playerView.angle = 0
    playerView.zoomfactor = 1
    gameData.basesBuilt = 0
    playerShip.oil = 1000
    starData.params = (random.random(),
                       random.random(),
                       random.random(),
                       random.random(),
                       random.random())
    Game()


###################################
#Returns A List Of Saved Games
def ListGames():
    return [file[:-4] for file in os.listdir(os.path.join("data", 'games')) if file.endswith(".pkl")]

###################################
#Opens A Certain Game File
def OpenGameFile(file, mode):
    return open(os.path.join("data", 'games', file+'.pkl'), mode)


###################################
#Loading A Saved Game
def Load():
    MenuList = [(file, file, 'button') for file in ListGames()]
    f = 0
    if LastGameLoaded:
        for i in range(len(MenuList)):
            if MenuList[i][0] == LastGameLoaded:
                f = i
    MenuList.append(('Cancel', 'cancel', 'cancelbutton'))
    result, data = menu.menu(Surface, MenuList, 20, 200, 10, 30, 35, 300, Font,f)
    if result != 'cancel':
        LoadGame(result)


###################################
#Load A Game
def LoadGame(Slot):
    global LastGameLoaded, playerShip, playerView, gameData, WreckContainer, ShipContainer, PlanetContainer, ArchiveContainer, starData
    LastGameLoaded = Slot
    f = OpenGameFile(Slot, 'rb')
    try:
        test = cPickle.load(f)
        if isinstance(test, str):
            if test == '0.9':
                playerShip = cPickle.load(f)
                playerView = cPickle.load(f)
                gameData = cPickle.load(f)
                ShipContainer = cPickle.load(f)
                WreckContainer = cPickle.load(f)
                PlanetContainer = cPickle.load(f)
                ArchiveContainer = cPickle.load(f)
                starData = cPickle.load(f)
        else:
            playerShip = test
            playerView = cPickle.load(f)
            gameData = cPickle.load(f)
            ShipContainer = cPickle.load(f)
            WreckContainer = []
            PlanetContainer = cPickle.load(f)
            ArchiveContainer = cPickle.load(f)
            starData = cPickle.load(f)
    except:
        f.close()
        Play('unselect')
    else:
        f.close()
        if Game() == 'exit':
            return 'exit'
        else:
            return 'to menu'

###################################
#Get A Filename To Save To
def SaveAs():
    global GamePaused
    GP = GamePaused
    GamePaused = True
    Clock = ABClock()
    if isinstance(LastGameLoaded, str):
        text = LastGameLoaded
    else:
        text = ''
    ticks = 0
    insertpos = len(text)
    Left = 35
    Top = 200
    printable = [ord(char) for char in 'abcdefghijklmnopqrstuvwxyz0123456789']
    FileList = ListGames()
    while True:
        Clock.tick(20)
        for event in pygame.event.get():
            if event.type == QUIT:
                GamePaused = GP
                return
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if insertpos > 0:
                        text = text[:insertpos-1] + text[insertpos:]
                        insertpos -= 1
                elif event.key == K_DELETE:
                    text = text[:insertpos] + text[insertpos+1:]
                elif event.key in printable:
                    text = text[:insertpos] + chr(event.key) + text[insertpos:]
                    insertpos += 1
                elif event.key == K_RETURN:
                    if text:
                        Save(text)
                    GamePaused = GP
                    return
                elif event.key == K_LEFT:
                    if insertpos > 0: insertpos -= 1
                elif event.key == K_RIGHT:
                    if insertpos < len(text): insertpos += 1
                elif event.key == K_HOME:
                    insertpos = 0
                elif event.key == K_END:
                    insertpos = len(text)
        Draw(False)
        ticks+= 1
        Y = Font.size(text)[1]
        pygame.draw.rect(Surface, (255, 255, 255), (Left, Top, 300, Y+4))
        pygame.draw.rect(Surface, (150, 150, 150), (Left, Top, 300, Y+4), 1)
        Surface.blit(Font.render('Save to: (leave empty to cancel)', 1, (255, 255, 255)),
                     (Left+2, Top-Y-3))
        Surface.blit(Font.render(text, 1, (0, 0, 0)),
                     (Left+2, Top))
        if (ticks//8)%2 == 0:
            X = Font.size(text[:insertpos])[0]
            pygame.draw.line(Surface, (0,0,0), (Left+2+X,Top+2), (Left+2+X,Top+Y), 1)
        #if ticks % 500 == 0:       #Uncomment this code
        #    FileList = ListGames() #to check for new games once in a while
        ypos = Top + Y + 8
        for file in FileList:
            if file.startswith(text):
                Surface.blit(Font.render(file, 1, (255, 255, 255)),
                             (Left+2, ypos))
                ypos += Y
        pygame.display.flip()


###################################
#Save The Current Game
def Save(Slot):
    global LastGameLoaded
    f = OpenGameFile(Slot, 'wb')
    cPickle.dump('0.9', f, -1)
    cPickle.dump(playerShip, f, -1)
    cPickle.dump(playerView, f, -1)
    cPickle.dump(gameData, f, -1)
    cPickle.dump(ShipContainer, f, -1)
    cPickle.dump(WreckContainer, f, -1)
    cPickle.dump(PlanetContainer, f, -1)
    cPickle.dump(ArchiveContainer, f, -1)
    cPickle.dump(starData, f, -1)
    f.close()
    LastGameLoaded = Slot


###################################
#The Main Game Loop
def Game():
    global Frames
    Clock = ABClock()
    while True:
        returnvalue = GetInput()
        if returnvalue == 'to menu':
            return
        elif returnvalue == 'exit':
            return 'exit'
        if GamePaused == False:
            if Move() == 'to menu':
                return
            Frames += 1
            Clock.tick(45)
        else:
            Clock.tick(10)
        Draw()


###################################
#Save Settings To File
def SaveSettings():
    f = open('data/settings.txt', 'w')
    f.write('Sound Volume\n\tMusic: %d\n\tEffects: %d\n'
            'Keys\n\tUp: %d\n\tLeft: %d\n\tRight: %d\n\tFire: %d\n\tLaunch: %d\n\tBuild: %d\n\tRepair: %d\n\tFill: %d\n\tPause: %d\n\tZoomOut: %d\n'
            '\tZoomIn: %d\n\tDrop: %d\nScreen\n\tMode: %s\n\tSize: %s\n\n'
            '#Default Keys:\n#Action\t\tKey\tCode\n#Speed Up\tUp\t273\n#Steer Left\tLeft\t276\n#Steer Right\tRight\t275\n#Fire\t\tSpace\t32\n'
            '#Launch\t\tRShift\t303\n#Build Base\tB\t98\n'
            '#Repair\t\tR\t114\n#Fill oil tank\tF\t102\n#Pause\t\tP\t112\n#Zoom out\tZ\t122\n#Zoom in\tA\t97\n#Drop\t\tD\t100\n#For other key codes, check pygame.locals'
            % (MUSIC_VOLUME, FX_VOLUME, KEY_UP, KEY_LEFT, KEY_RIGHT, KEY_FIRE, KEY_LAUNCH, KEY_BUILD, KEY_REPAIR, KEY_FILL, KEY_PAUSE, KEY_ZOOMOUT, KEY_ZOOMIN, KEY_DROP, 'Full' if SCR_FULL else 'Windowed', 'x'.join(str(i) for i in SCR_SIZE)))
    f.close()


###################################
#The Main Loop
def Main():
    Play('music')
    while True:
        result = Menu()
        if result == 'new':
            if SetUpGame() == 'exit':
                break
        elif result == 'continue':
            if Game() == 'exit':
                break
        elif result == 'load':
            if Load() == 'exit':
                break
        elif result == 'intro':
            if Intro() == 'exit':
                break
        elif result == 'options':
            r = Options()
            SaveSettings()
            if r == 'exit':
                break
        elif result == 'exit':
            break
    pygame.quit()


###################################
#Set Up Window
pygame.display.set_caption("SpaceFlight2D")
icon = pygame.Surface((1,1)); icon.set_alpha(0); pygame.display.set_icon(icon)
Surface = pygame.display.set_mode(SCR_SIZE, SCR_FULL and FULLSCREEN)

if __name__ == '__main__': Main()
