from card import *

# Common
class SpeedUp(Card):
    name = "speed up"
    basePrice = 50
    desc = "Speed up!"
    def on_pickup(self):
        self.player.speed += 20

class IFrameUp(Card):
    name = "Invincibility Up"
    basePrice = 50
    desc = "More IFrames!"
    def on_pickup(self):
        self.player.iFrames += 0.5

class BulletSize(Card):
    name = "Bigger Bullets"
    basePrice = 50
    desc = "What do you think it does?"
    def on_pickup(self):
        self.player.bulletSize *= 2
        
class DamageUp(Card):
    name = "damage up"
    desc = "Damage up!"
    basePrice = 150
    def on_pickup(self):
        self.player.dmg += 2
        self.player.baseDmg = self.player.dmg

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
        self.player.baseAtkRate = self.player.baseAtkRate

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
class TrueHit(Card):
    name = "True Hit"
    basePrice = 250
    desc = "Remove all enemy IFrames"
    def on_pickup(self):
        self.player.truehit = True

class Shield(Card):
    name = "Shield"
    basePrice = 100
    desc = "+1 free hit per round"
    def on_pickup(self):
        self.player.shield += 1
        self.player.curr_shield = self.player.shield

class Scope(Card):
    name = "Sniper Scope"
    basePrice = 200
    desc = "Accuracy Up and a little assitance"
    def on_pickup(self):
        self.player.scope = True
        # accuracy up part
        self.player.inaccuracy *= 0.66
        if self.player.inaccuracy < 0:
            self.player.inaccuracy = 0

class Firewall(Card):
    name = "Firewall"
    basePrice = 300
    desc = "Immunity to fire"
    def on_pickup(self):
        self.player.fire_immunity = True

class RubberBullets(Card):
    name = "Rubber Bullets"
    basePrice = 125
    desc = "Still lethal, just bouncier! (+1 bounce)"
    def on_pickup(self):
        self.player.bouncy_bullets = True
        self.player.piercing += 1

class StaticDischarge(Card):
    name = "Static Discharge"
    basePrice = 350
    desc = "blast on hit"
    def on_pickup(self):
        self.player.static_discharge += 1

class LifeStealUp(Card):
    name = "life steal up"
    basePrice = 350
    desc = "Life steal up!"
    def on_pickup(self):
        self.player.lifesteal += 1

class HotShot(Card):
    name = "Hot shot"
    basePrice = 200
    desc = "+1 Stack of fire on enemy hit"
    def on_pickup(self):
        self.player.hotShot += 1

# i think shotgun should apply a dmg multiplier but idk
class Shotgun(Card):
    name = "shotgun"
    basePrice = 150
    desc = "SHOTGUN MOMENT"
    def on_pickup(self):
        self.player.bulletCount += 3
        self.player.dmg *= 0.6
        self.player.baseDmg = self.player.dmg
        self.player.inaccuracy += 0.1
        self.player.speedInaccuracy += 0.1
        self.player.atkRateMultiplier /= 3

class Piercing(Card):
    name = "piercing up"
    basePrice = 150
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
        self.player.dmgMultiplier = 0.5
        self.player.inaccuracy += 0.06
        self.player.speedInaccuracy += 0.3
        self.player.atkRateMultiplier *= 5
        self.player.bulletSpeed *= 1.5

class DoubleShot(Card):
    name = "Bullet count up"
    basePrice = 250
    desc = "Extra bullet!"
    def on_pickup(self):
        self.player.bulletCount += 1

class CoinGun(Card):
    name = "Coin Gun"
    basePrice = 500
    desc = "Double damage at a cost..."
    def on_pickup(self):
        self.player.dmgMultiplier *= 2
        self.player.coin_gun += 1

class Resistance(Card):
    name = "Resistance"
    basePrice = 350
    desc = "20% damage reduction!"
    def on_pickup(self):
        self.player.dmg_take_multiplier *= 0.8

class BloodBullets(Card):
    name = "Blood Bullets"
    basePrice = 350
    desc = "Damage way up, Firerate up, bullets cost health!"
    def on_pickup(self):
        self.player.blood_bullets += 1
        self.player.dmgMultiplier *= 2.5
        self.player.atkRateMultiplier *= 1.5

class Homing(Card):
    name = "Homing"
    basePrice = 350
    desc = "Bullets home in on nearby enemies"
    def on_pickup(self):
        self.player.homing += 1
        self.player.bulletSpeed *= 0.7

class Phoenix(Card):
    name = "System Reboot"
    basePrice = 350
    desc = "On death, kill all enemies on screen and revive with full health and x2 damage and firerate for short duration"
    def on_pickup(self):
        self.player.phoenix = True

PASSIVE_CARDS = {
    "common":[
        SpeedUp, DamageUp, AccuracyUp,
        AttackSpeedUp, BulletSpeedUp, MaxHealthUp,
        IFrameUp, BulletSize
    ],
    "rare":[
        Shotgun, Piercing, LifeStealUp,
        Panic, HotShot, Shield,
        StaticDischarge, Firewall, RubberBullets,
        Scope, TrueHit
    ],
    "legendary":[
        DoubleShot, Minigun, Resistance,
        CoinGun, BloodBullets, Phoenix,
        Homing,
    ],
    "devil_deal":[ # definitely not stealing from isaac
    ],
}

