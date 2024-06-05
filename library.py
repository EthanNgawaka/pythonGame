import pygame
import random
import math
import time

def scalMult(vec, scal):
    return [vec[0]*scal, vec[1]*scal]

def add(a, b):
    return [a[0]+b[0], a[1]+b[1]]

def subtract(a, b):
    return [a[0]-b[0], a[1]-b[1]]

def magnitude(a):
    return math.sqrt(a[0]**2 + a[1]**2)

def init(windowW, windowH, caption):
    pygame.init()
    window = pygame.display.set_mode((windowW,windowH))
    pygame.display.set_caption(caption)
    return window

def drawRect(window, rect, col, width=0): # col = (R, G, B)
    pygame.draw.rect(window, col, pygame.Rect(*rect), width)

def drawCircle(window, circle, col): # circle = (center, radius)
    pygame.draw.circle(window, col, circle[0], circle[1])

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

