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
        self.rect = [x, y, 10, 10]
        self.vel = vel
        self.col = (255, 255, 0)
        self.distThreshold = 150

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

        if AABBCollision(player.rect, self.rect):
            player.coins+=1
            print(player.coins)
            coinManager.coins.remove(self)

    def draw(self, window):
        drawRect(window, self.rect, self.col)
