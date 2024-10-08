import pygame
import pygame._sdl2 as pg_sdl2
import random
import math
import time

#W = 1920
#H = 1080
W = 1540
H = 870

keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")

def getRectCenter(rect):
    return [rect[0]+rect[2]/2, rect[1]+rect[3]/2]

class ShadowManager:
    def __init__(self):
        self.shadows = [] # a shadow has a pos, radius, and col [[x,y],r,(r,g,b,a)]
        self.surface = pygame.Surface((W, H), pygame.SRCALPHA)

    def renderShadows(self):
        for shadow in self.shadows:
            pygame.draw.circle(self.surface, shadow[2], [shadow[0][0]-camera.pos[0], shadow[0][1]-camera.pos[1]], shadow[1])

        self.shadows = []
    
    def addShadowToRender(self, pos, r, col):
        self.shadows.append([pos, r, col])

    def draw(self, window):
        self.surface.fill((0,0,0,0))
        self.renderShadows()
        window.blit(self.surface, (0, 0))

shadowManager = ShadowManager()

class Mouse:
    def __init__(self):
        self.pressed = [False,False]
        self.down = [False,False]
        self.x = 0
        self.y = 0
    
    def update(self):
        self.pressed = [False,False]
        mousePos = pygame.mouse.get_pos()
        self.x = mousePos[0]
        self.y = mousePos[1]
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

mouse = Mouse()
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

def lerp(i, j, t):
    return i * (1-t) + j*t

def rectLerp(rect1, rect2, t):
    outputX = lerp(rect1[0], rect2[0], t)
    outputY = lerp(rect1[1], rect2[1], t)
    return [outputX, outputY, rect1[2], rect1[3]]

def vecLerp(vec1, vec2, t):
    return [lerp(vec1[0], vec2[0], t), lerp(vec1[1], vec2[1], t)] 

def scalMult(vec, scal):
    return [vec[0]*scal, vec[1]*scal]

def addRects(a,b):
    return [a[0]+b[0], a[1]+b[1], a[2]+b[2], a[3]+b[3]]

def add(a, b):
    return [a[0]+b[0], a[1]+b[1]]

def subtractRects(a,b):
    return [a[0]-b[0], a[1]-b[1], a[2]-b[2], a[3]-b[3]]

def subtract(a, b):
    return [a[0]-b[0], a[1]-b[1]]


def magnitude(a):
    return math.sqrt(a[0]**2 + a[1]**2)

def init(windowW, windowH, caption):
    pygame.init()
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
        window.blit(pygame.transform.scale(self.img, (self.w, self.h)), (self.x-camera.pos[0], self.y-camera.pos[1]))

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

def drawText(window, string, col, pos, size, drawAtCenter=False, drawAsUI=False):
    font = pygame.font.SysFont("Arial",size)
    img = font.render(string, True, col)

    if drawAsUI:
        drawPos = pos
    else:
        drawPos = subtract(pos, camera.pos)

    if drawAtCenter:
        textRect = img.get_rect()
        textRect.center = drawPos
        window.blit(img, textRect)
    else:
        window.blit(img, drawPos)

def drawRect(window, rect, col, width=0): # col = (R, G, B, [A])
    #pygame.draw.rect(window, col, pygame.Rect(*subtractRects(rect,camera.getRect())), width)

    s = pygame.Surface((rect[2], rect[3]))
    try:
        s.set_alpha(col[3])
    except IndexError: # No alpha given
        pass
    
    s.fill((col[0],col[1],col[2]))
    window.blit(s, (rect[0]-camera.pos[1], rect[1]-camera.pos[0]))

def drawCircle(window, circle, col): # circle = (center, radius)
    pygame.draw.circle(window, col, subtract(circle[0], camera.pos), circle[1])

def enlargeRect(inputRect, a, b, preserveBottomVerticesY=False):
    rect = inputRect
    transVec = [0,0]
    if preserveBottomVerticesY:
        transVec = [-(rect[0]+rect[2]/2),-(rect[1]+rect[3])]
    else:
        transVec = [-(rect[0]+rect[2]/2),-(rect[1]+rect[3]/2)]

    vertices = [
        [rect[0],rect[1]],
        [rect[0]+rect[2],rect[1]],
        [rect[0]+rect[2],rect[1]+rect[3]],
        [rect[0], rect[1]+rect[3]]
    ]

    for i in range(len(vertices)):
        vertices[i] = add(vertices[i], transVec)

    L = [[a,0],[0,b]];

    for i in range(len(vertices)):
        vertices[i] = [a*vertices[i][0], b*vertices[i][1]]
    
    for i in range(len(vertices)):
        vertices[i] = subtract(vertices[i], transVec);

    rect = [vertices[0][0],vertices[0][1],vertices[1][0]-vertices[0][0],vertices[2][1]-vertices[0][1]]
    return rect;
