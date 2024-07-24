import pygame
import pygame._sdl2 as pg_sdl2
import random
import math
import time

W = 1920
H = 1080

keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")

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

def drawRect(window, rect, col, width=0): # col = (R, G, B)
    pygame.draw.rect(window, col, pygame.Rect(*subtractRects(rect,camera.getRect())), width)

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
