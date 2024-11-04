from card import *

# Common
class SpeedUp(Card):
    def __init__(self):
        super().__init__("speed up", 50)
    def on_pickup(self):
        self.player.speed += 20
        
class DamageUp(Card):
    def __init__(self):
        super().__init__("damage up", 150)
    def on_pickup(self):
        self.player.dmg += 3

class AccuracyUp(Card):
    def __init__(self):
        super().__init__("accuracy up", 100)
    def on_pickup(self):
        self.player.inaccuracy -= 0.1
        
class AttackSpeedUp(Card):
    def __init__(self):
        super().__init__("Attack speed up", 100)
    def on_pickup(self):
        self.player.atkRate *= 0.9

class BulletSpeedUp(Card):
    def __init__(self):
        super().__init__("bullet speed up", 50)
    def on_pickup(self):
        self.player.bulletSpeed += 10

class MaxHealthUp(Card):
    def __init__(self):
        super().__init__("max health up", 50)
    def on_pickup(self):
        self.player.maxHealth += 20
        self.player.health += 20


# Rare
class LifeStealUp(Card):
    def __init__(self):
        super().__init__("life steal up", 150)
    def on_pickup(self):
        self.player.lifesteal += 1

class Shotgun(Card):
    def __init__(self):
        super().__init__("shotgun", 175)
    def on_pickup(self):
        self.player.bulletCount += 3
        self.player.dmg /= 2
        self.player.inaccuracy += 0.1
        self.player.speedInaccuracy += 0.1
        self.player.atkRate += 0.1

class Piercing(Card):
    def __init__(self):
        super().__init__("piercing up", 150)
    def on_pickup(self):
        self.player.piercing += 1

# Legendary
class Minigun(Card):
    def __init__(self):
        super().__init__("Minigun", 250)
    def on_pickup(self):
        self.player.dmgMultiplier = 0.2
        self.player.inaccuracy += 0.1
        self.player.speedInaccuracy += 0.3
        self.atkRateMultiplier = 5
        self.bulletSpeed += 100

class DoubleShot(Card):
    def __init__(self):
        super().__init__("Bullet count up", 250)
    def on_pickup(self):
        self.player.bulletCount += 1

