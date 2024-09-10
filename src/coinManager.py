import sys
import os
from world import *
from scene import *

sys.path.append(os.path.abspath("../lib"))

from library import *

class CoinManager(Entity):
    def __init__(self, gameRef):
        super().__init__("CoinManager", [0,0,0,0], "Manager", gameRef)
        self.coins = []

    def draw(self, window):
        pass

    def update(self, dt):
        pass

    def spawnCoin(self, x, y, qty):
        for i in range(qty):
            theta = random.randint(0,360)*math.pi/180
            vel = scalMult([math.cos(theta), math.sin(theta)],random.randint(0,20))
            self.coins.append(Coin(x, y, vel, self.game))
            self.game.curr_world.add_entity(self.coins[len(self.coins)-1])

class Coin(RigidBody):
    def __init__(self, x, y, vel, game):
        rect = [x, y, 40, 40]
        ID = f"coin#{random.randint(0,999)}"
        super().__init__(ID, rect, "Coin", game, 0)
        self.airFric = 0.9

        self.vel = np.array(vel)
        self.distThreshold = 150

        self.img = Image("assets/coin.png", x,y, 16,16)

    def update(self, dt):
        player = self.game.curr_world.entities["Player"]["player"]
        attractionSpeed = 1
        distVec = subtract(player.rect, self.rect)
        mag = magnitude(distVec)
        if mag < self.distThreshold:
            self.distThreshold = 2000
            if mag > 0:
                self.apply_impulse(scalMult(distVec,attractionSpeed/mag))
        
        super().update(dt)
        #TODO: use onScreen to make coins bounce agains wall

    def draw(self, window):
        self.img.setRect(self.rect)
        self.img.draw(window)

    def on_collision(self, otherEntity):
        player = self.game.curr_world.entities["Player"]["player"]
        manager = self.game.curr_world.entities["Manager"]["CoinManager"]
        player.coins += 1
        try:
            manager.coins.remove(self)
            self.game.curr_world.delete_entity(self)
        except ValueError as e:
            print(e)
            print("for some reason the coin didnt delete properly so its trying to again")
