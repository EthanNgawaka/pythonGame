import pygame
import pygame._sdl2 as pg_sdl2
import random
import math
import time
import cProfile, pstats, io

#W = 1920
#H = 1080
W = 1540
H = 870

DEBUG = True

def profile(fnc):
    """A decorator that uses cProfile to profile a function"""
    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


# classes TODO( need to seperate these out )
class Mouse:
    def __init__(self):
        self.pressed = [False,False]
        self.down = [False,False]
        self.pos = pygame.Vector2()
        self.rect = pygame.Rect(0,0,0,0)
    
    def update(self):
        self.pressed = [False,False]
        mousePos = pygame.mouse.get_pos()
        self.pos.x = mousePos[0]
        self.pos.y = mousePos[1]
        self.rect = pygame.Rect(self.pos.x,self.pos.y,0,0)
        pressed = pygame.mouse.get_pressed(num_buttons=3)
        if pressed[0]:
            if self.down[0]:
                self.pressed[0] = False
            else:
                self.pressed[0] = True
            self.down[0] = True
        else:
            self.down[0] = False

        if pressed[1]:
            if self.down[1]:
                self.pressed[1] = False

            else:
                self.pressed[1] = True
            self.down[1] = True
        else:
            self.down[1] = False

# TODO( integrate with game class )
class Camera:
    def __init__(self, trackingEasing=0.1):
        self.pos = [0,0]
        self.target = [0,0]
        self.shakeTimer = 0
        self.shakeIntensity = 0
        self.trackingEasing = trackingEasing
        self.shakeEasing = 0.5
    
    def setTarget(self, targetVec):
        self.target = targetVec

    def shake(self, intensity=20, duration=0.2, shakeEasing=0.6):
        self.shakeTimer = duration
        self.shakeIntensity = intensity
        self.shakeEasing = shakeEasing

    def getRect(self):
        return [self.pos[0], self.pos[1], 0, 0]

    def update(self, dt):
        self.pos = vecLerp(self.pos, self.target, self.trackingEasing)

        if self.shakeTimer > 0:
            self.shakeTimer -= dt
            shakeVec = [random.uniform(-1,1)*self.shakeIntensity, random.uniform(-1,1)*self.shakeIntensity]
            self.pos = vecLerp(self.pos, add(self.pos,shakeVec), self.shakeEasing)
camera = Camera()

# currently no support for multiple controllers it just uses the first one connected
"""
A Button        - Button 0
B Button        - Button 1
X Button        - Button 2
Y Button        - Button 3
Left Bumper     - Button 4
Right Bumper    - Button 5
Back Button     - Button 6
Start Button    - Button 7
L. Stick In     - Button 8
R. Stick In     - Button 9
Guide Button    - Button 10

Left Stick:
Left -> Right   - Axis 0
Up   -> Down    - Axis 1

Right Stick:
Left -> Right   - Axis 3
Up   -> Down    - Axis 4

Left Trigger:
Out -> In       - Axis 2

Right Trigger:
Out -> In       - Axis 5

Eg)
joystick.get_button(0) -> true if A button is down
joystick.get_axis(0) -> returns -1 to 1 based on left stick input

"""
class Controller:
    def __init__(self):
        self.joysticks = []
        self.LSTICK = [0,0]
        self.RSTICK = [0,0]
        self.A = 0
        self.B = 0
        self.X = 0
        self.Y = 0
        self.START = 0

        self.buttons = {"a":0, "b":1, "x":2, "y":3, "start":7}
        self.connected = False

        self.deadzone_range = 0.1

    def get_pressed(self, key):
        return getattr(self, key.upper()) == 1

    def get_down(self, key):
        return getattr(self, key.upper()) > 0

    def check_controllers_connected(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                self.joysticks.append(joy)

    def update(self):
        if not self.connected:
            self.check_controllers_connected()
            if len(self.joysticks) > 0:
                self.connected = True
            return

        joy = self.joysticks[0]

        for btn in self.buttons:
            btn_num = self.buttons[btn]
            if joy.get_button(btn_num):
                setattr(self, btn.upper(), getattr(self,btn.upper())+1)
                continue

            setattr(self, btn.upper(), 0)

        """ rounded to 1 decimal to stop drifting? idk what best practice is
        self.LSTICK = [round(joy.get_axis(0), 1), round(joy.get_axis(1), 1)]
        self.RSTICK = [round(joy.get_axis(2), 1), round(joy.get_axis(3), 1)]
        """
        self.LSTICK = [joy.get_axis(0),joy.get_axis(1)]
        self.RSTICK = [joy.get_axis(2),joy.get_axis(3)]
        if abs(self.LSTICK[0]) < self.deadzone_range:
            self.LSTICK[0] = 0
        if abs(self.LSTICK[1]) < self.deadzone_range:
            self.LSTICK[1] = 0
        if abs(self.RSTICK[0]) < self.deadzone_range:
            self.RSTICK[0] = 0
        if abs(self.RSTICK[1]) < self.deadzone_range:
            self.RSTICK[1] = 0

class Image:
    def __init__(self, src, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = pygame.image.load(src).convert()
        self.img.set_colorkey((0,255,0))
        self.sprite = pygame.Surface((self.img.get_width(),self.img.get_height()))
        self.sprite.blit(self.img, (0,0))

    def setRect(self, newRect):
        self.x = newRect[0]
        self.y = newRect[1]
        self.w = newRect[2]
        self.h = newRect[3]

    def draw(self, window):
        window.blit(pygame.transform.scale(self.img, (self.w, self.h)), (self.x, self.y))

class Spritesheet:
    def __init__(self, rect, src, spriteSize, secsBetweenFrames, bounce=False): # ([x,y,w,h], filename, [spriteW, spriteH], fps)
        self.src = src
        self.rect = rect
        self.sprite_sheet = pygame.image.load(src)
        self.spriteW = spriteSize[0]
        self.spriteH = spriteSize[1]

        self.timer = 0
        self.secsBetweenFrames = secsBetweenFrames
        self.currFrame = 0
        self.bounce = bounce
        self.animationDir = 1

        self.state = ""
        self.states = {} #{"state_name":[frames, correspondingLine]}
        self.rotation = 0

    def rotate(self, rotation):
        self.rotation = rotation

    def addState(self, state_name, correspondingLine, frames):
        self.states[state_name] = [frames, correspondingLine]
        self.state = state_name

    def setState(self, state_name, reset=True):
        if self.state != state_name:
            self.state = state_name
            self.currFrame = 0
            self.animationDir = 1

    def draw(self, rect, window, rotateAround=[0,0]):
        self.rect = rect
        scaledImage = pygame.transform.scale(self.get_curr_sprite(), (self.rect[2], self.rect[3]))
        scaledAndRotatedImage = pygame.transform.rotate(scaledImage, self.rotation)

        centerPos = (self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2)
        if rotateAround[0] != 0 and rotateAround[1] != 0:
            centerPos = (rotateAround[0], rotateAround[1])

        newRect = scaledAndRotatedImage.get_rect(center=centerPos)

        window.blit(scaledAndRotatedImage, newRect.topleft)
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.secsBetweenFrames:
            self.currFrame += self.animationDir
            self.timer = 0

            if self.bounce:
                if self.currFrame == 0 or self.currFrame >= self.states[self.state][0]-1:
                    self.animationDir*=-1
            else:
                if self.currFrame >= self.states[self.state][0]:
                    self.currFrame = 0

    def get_sprite(self, x, y):
        sprite = pygame.Surface((self.spriteW, self.spriteH))
        sprite.set_colorkey((0,255,0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, self.spriteW, self.spriteH))
        return sprite

    def get_curr_sprite(self):
        state = self.states[self.state]
        return self.get_sprite(self.currFrame*self.spriteW, state[1]*self.spriteH)

# init funcs
def init(windowW, windowH, caption):
    pygame.init()
    pygame.joystick.init()
    window = pygame.display.set_mode((windowW,windowH))#, flags=pygame.SCALED | pygame.HIDDEN)
    #display_info = pygame.display.Info()
    #SCALE = (display_info.current_w/windowW, display_info.current_h/windowH)
    #nativeWindow = pg_sdl2.Window.from_display_module()
    #nativeWindow.size = (windowW * SCALE[0], windowH * SCALE[1])
    #nativeWindow.position = pg_sdl2.WINDOWPOS_CENTERED
    #nativeWindow.show()

    #pygame.display.toggle_fullscreen()
    pygame.display.set_caption(caption)
    return window

# misc math funcs
def vec_angle_to(A, B):
    AtoB = B - A
    return math.atan2(AtoB.y, AtoB.x)
def degs_to_rads(degs):
    return math.pi*degs/180
def rads_to_degs(rads):
    return 180*rads/math.pi
def lerp(i, j, t):
    return i * (1-t) + j*t
def AABBCollision(rect1, rect2): # rect = (x,y,w,h) returns min trans vec if true
    # actual aabb logic, never done it in a list b4 thought itd look neater
    checks = [
        (rect1[0]+rect1[2] >= rect2[0]), (rect1[0] <= rect2[0]+rect2[2]),
        (rect1[1]+rect1[3] >= rect2[1]), (rect1[1] <= rect2[1] + rect2[3])
    ]
    for check in checks:
        if not check:
            return False

    ytv21 = rect2[1] - (rect1[1]+rect1[3])
    ytv12 = (rect2[1]+rect2[3]) - rect1[1]

    xtv21 = rect2[0] - (rect1[0]+rect1[2])
    xtv12 = (rect2[0]+rect2[2]) - rect1[0] 
    
    ytv = ytv21 if abs(ytv21) < abs(ytv12) else ytv12
    xtv = xtv21 if abs(xtv21) < abs(xtv12) else xtv12
    
    mtv = (xtv,0) if abs(xtv) < abs(ytv) else (0,ytv)
    return mtv

# so i didnt realise font drawing was SO FUCKING EXPENSIVE
# create a new img to blit every frame is real bad but
# improves by about 4x with caching
# a font img is uniquely determined by its string, col and size
# if exists use it if not create it and add it to cached fonts
cached_fonts = {}
# drawing funcs
def drawText(window, string, col, pos, size, drawAtCenter=False, drawAsUI=False):
    font = pygame.font.SysFont("Arial",size)
    if (string, col, size) in cached_fonts:
        img = cached_fonts[(string, col, size)]
    else:
        img = font.render(string, True, col)
        cached_fonts[(string, col, size)] = img

    if drawAsUI:
        drawPos = pos
    else:
        drawPos = pos

    if drawAtCenter:
        textRect = img.get_rect()
        textRect.center = drawPos
        window.blit(img, textRect)
    else:
        window.blit(img, drawPos)

def drawRect(window, rect, col_obj, outline_thickness=0):
    # col = (R, G, B, [A])
    # col_obj = (fill_col, outline_col)
    # can just pass fill_col if outline_thickness is left as 0
    # so it turns out creating a new surface a million times a frame is kinda ass soooo
    # back to basics

    col = col_obj
    out_col = None
    if outline_thickness > 0:
        col = col_obj[1]
        out_col = col_obj[0]

    if len(col) == 4 and col[3]/255 < 1: # alpha is provided
        # while creating a new surface constantly is bad
        # for an alpha it is still necessary so IF there is a transparent object then
        # do the surface version
        s = pygame.Surface((rect[2], rect[3]))
        s.set_alpha(col[3])
        s.fill((col[0],col[1],col[2]))

        if outline_thickness > 0:
            s.fill((out_col[0],out_col[1],out_col[2]), s.get_rect().inflate(-outline_thickness, -outline_thickness))

        window.blit(s, (rect[0], rect[1]))
        return
        
    # just draw the goddamn rectangle
    pygame.draw.rect(window, col, rect)
    if outline_thickness > 0:
        pygame.draw.rect(window, out_col, rect, outline_thickness)


def drawCircle(window, circle, col): # circle = (center, radius)
    pygame.draw.circle(window, col, circle[0], circle[1])

