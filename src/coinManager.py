import sys
import os

sys.path.append(os.path.abspath("../lib"))

from library import *

class CoinManager:
    def __init__(self):
        self.coins = []

    def draw(self, window):
        for coin in self.coins:
            coin.draw(window)

    def update(self, dt, player):
        for coin in self.coins:
            coin.update(dt, player, self)

    def spawnCoin(self, x, y, qty):
        for i in range(qty):
            theta = random.randint(0,360)*math.pi/180
            vel = scalMult([math.cos(theta), math.sin(theta)],random.randint(0,500))
            self.coins.append(Coin(x, y, vel))

class Coin:
    def __init__(self, x, y, vel):
        self.rect = [x, y, 40, 40]
        self.vel = vel
        self.distThreshold = 150

        self.img = Image("assets/coin.png", x,y, 16,16)

    def update(self, dt, player, coinManager):
        attractionSpeed = 60
        distVec = subtract(player.rect, self.rect)
        mag = magnitude(distVec)
        if mag < self.distThreshold:
            self.distThreshold = 999
            if mag > 0:
                self.vel = add(self.vel, scalMult(distVec,attractionSpeed/mag))

        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel = scalMult(self.vel, 0.9)
        if AABBCollision((0, 0, 1920, 5),self.rect) and self.vel[1] < 0:
            self.vel[1] = 0
        if AABBCollision((0, 1080-5, 1920, 5),self.rect) and self.vel[1] > 0:
            self.vel[1] = 0
        if AABBCollision((0, 0, 5, 1080),self.rect) and self.vel[0] < 0:
            self.vel[0] = 0
        if AABBCollision((1920-5, 0, 5, 1080),self.rect) and self.vel[0] > 0:
            self.vel[0] = 0

        if AABBCollision(player.rect, self.rect):
            player.coins+=1
            coinManager.coins.remove(self)

        shadowManager.addShadowToRender(add(getRectCenter(self.rect), [-self.rect[2]/10,self.rect[3]/10]), self.rect[3]*0.36, (59,52,7,128))

    def draw(self, window):
        self.img.setRect(self.rect)
        self.img.draw(window)
