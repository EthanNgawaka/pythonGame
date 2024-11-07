from card import *

# Common
class SpeedUp(Card):
    name = "speed up"
    basePrice = 50
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.speed += 20
        
class DamageUp(Card):
    name = "damage up"
    basePrice = 150
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.dmg += 3

class AccuracyUp(Card):
    name = "accuracy up"
    basePrice = 100
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.inaccuracy -= 0.1
        if self.player.inaccuracy < 0:
            self.player.inaccuracy = 0
        
class AttackSpeedUp(Card):
    name = "Attack speed up"
    basePrice = 100
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.atkRate *= 0.9

class BulletSpeedUp(Card):
    name = "bullet speed up"
    basePrice = 50
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.bulletSpeed += 10

class MaxHealthUp(Card):
    name = "max health up"
    basePrice = 50
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.maxHealth += 20
        self.player.health += 20


# Rare
class LifeStealUp(Card):
    name = "life steal up"
    basePrice = 150
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.lifesteal += 1

class Shotgun(Card):
    name = "shotgun"
    basePrice = 175
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.bulletCount += 3
        self.player.dmg /= 2
        self.player.inaccuracy += 0.1
        self.player.speedInaccuracy += 0.1
        self.player.atkRate += 0.1

class Piercing(Card):
    name = "piercing up"
    basePrice = 150
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.piercing += 1

# Legendary
class Minigun(Card):
    name = "Minigun"
    basePrice = 250
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.dmgMultiplier = 0.2
        self.player.inaccuracy += 0.06
        self.player.speedInaccuracy += 0.3
        self.player.atkRateMultiplier = 5
        self.player.bulletSpeed *= 1.5

class DoubleShot(Card):
    name = "Bullet count up"
    basePrice = 250
    def __init__(self):
        super().__init__()
    def on_pickup(self):
        self.player.bulletCount += 1

