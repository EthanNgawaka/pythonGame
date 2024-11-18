from card import *

# Common
class SpeedUp(Card):
    name = "speed up"
    basePrice = 50
    desc = "Speed up!"
    def on_pickup(self):
        self.player.speed += 20
        
class DamageUp(Card):
    name = "damage up"
    desc = "Damage up!"
    basePrice = 150
    def on_pickup(self):
        self.player.dmg += 2

class AccuracyUp(Card):
    name = "accuracy up"
    desc = "Accuracy up!"
    basePrice = 100
    def on_pickup(self):
        self.player.inaccuracy *= 0.66
        if self.player.inaccuracy < 0:
            self.player.inaccuracy = 0
        
class AttackSpeedUp(Card):
    name = "Attack speed up"
    desc = "Attack Speed up!"
    basePrice = 100
    def on_pickup(self):
        self.player.atkRate *= 0.8

class BulletSpeedUp(Card):
    name = "bullet speed up"
    desc = "Bullet Speed up!"
    basePrice = 50
    def on_pickup(self):
        self.player.bulletSpeed += 10

class MaxHealthUp(Card):
    name = "max health up"
    desc = "Max Health up!"
    basePrice = 50
    def on_pickup(self):
        self.player.maxHealth += 20
        self.player.health += 20


# Rare
class LifeStealUp(Card):
    name = "life steal up"
    basePrice = 150
    desc = "Life steal up!"
    def on_pickup(self):
        self.player.lifesteal += 1

class HotShot(Card):
    name = "Hot shot"
    basePrice = 125
    desc = "+1 Stack of fire on enemy hit"
    def on_pickup(self):
        self.player.hotShot += 1

# i think shotgun should apply a dmg multiplier but idk
class Shotgun(Card):
    name = "shotgun"
    basePrice = 175
    desc = "SHOTGUN MOMENT"
    def on_pickup(self):
        self.player.bulletCount += 3
        self.player.dmg *= 0.4
        self.player.inaccuracy += 0.1
        self.player.speedInaccuracy += 0.1
        self.player.atkRate += 0.1

class Piercing(Card):
    name = "piercing up"
    basePrice = 200
    desc = "Piercing up!"
    def on_pickup(self):
        self.player.piercing += 1
        self.player.kb /= 2 # half kb

class Panic(Card):
    name = "panic"
    basePrice = 150
    desc = "+2% permanent speed on hit!"
    def on_pickup(self):
        self.player.panic += 1

# Legendary
class Minigun(Card):
    name = "Minigun"
    basePrice = 250
    desc = "It's a minigun, what more do you want?"
    def on_pickup(self):
        self.player.dmgMultiplier = 0.4
        self.player.inaccuracy += 0.06
        self.player.speedInaccuracy += 0.3
        self.player.atkRateMultiplier = 5
        self.player.bulletSpeed *= 1.5

class DoubleShot(Card):
    name = "Bullet count up"
    basePrice = 250
    desc = "Extra bullet!"
    def on_pickup(self):
        self.player.bulletCount += 1

PASSIVE_CARDS = {
    "common":[
        SpeedUp, DamageUp, AccuracyUp,
        AttackSpeedUp, BulletSpeedUp, MaxHealthUp
    ],
    "rare":[
        Shotgun, Piercing, LifeStealUp, Panic, HotShot
    ],
    "legendary":[
        DoubleShot, Minigun
    ],
}

