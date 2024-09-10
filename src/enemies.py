import sys
import os

sys.path.append(os.path.abspath("../lib"))

from library import *
from player import *
from particles import *
from world import *
from scene import *

class Enemy(RigidBody):
    def __init__(self, rect, type, gameRef):
        ID = f"enemy_{type}#{random.randint(0,9999)}"
        super().__init__(ID, rect, "Enemy", gameRef)

    def boundEnemy(self): #TODO: replace with onScreen() function
        leftCheck = self.rect[0] < -self.rect[2] and self.vel[0] < 0
        rightCheck = self.rect[0] > W+self.rect[2] and self.vel[0] > 0
        if leftCheck or rightCheck:
            self.vel[0] *= -1

        upCheck = self.rect[1] < -self.rect[3] and self.vel[1] < 0
        downCheck = self.rect[1] > H+self.rect[3] and self.vel[1] > 0
        if upCheck or downCheck:
            self.vel[1] *= -1    

    def handle_collision_with_player(self, playerRef):
        relPos = np.subtract(self.rect, playerRef.rect)
        knockbackVec = scalMult(relPos, self.contactKnockback * (1/magnitude(relPos)))
        playerKB = np.multiply(-2, np.array(knockbackVec))
        playerRef.takeDmg(self.contactDmg,  playerKB)

        self.apply_impulse(np.multiply(0.4, np.array(knockbackVec)))
        self.stunTimer = self.stunTime

    def handle_collision_with_bullet(self, bullet):
        # handle diff damage/bullet types
        if bullet.type == "haloBullet":
            self.health -= self.playerRef.dmg*self.playerRef.dmgMultiplier*4
        else:
            self.health -= self.playerRef.dmg*self.playerRef.dmgMultiplier

        # become invincible
        self.iFrames = self.iFramesMax

        # do knockback if u can
        relPos = np.subtract(self.rect, self.playerRef.rect)
        knockbackVec = scalMult(relPos, 5 * (1/magnitude(relPos)))
        if magnitude(relPos) != 0:
            self.apply_impulse(knockbackVec)
            self.stunTimer = self.stunTime
        
        # player lifesteal TODO: move this to player side
        if self.playerRef.health < self.playerRef.maxHealth:
            self.playerRef.health += self.playerRef.lifeSteal
            if self.playerRef.health > self.playerRef.maxHealth:
                self.playerRef.health = self.playerRef.maxHealth

        if self.health <= 0:
            self.die()

    def on_collision(self, otherEntity):
        if isinstance(otherEntity, Bullet) and self.iFrames <= 0:
            self.handle_collision_with_bullet(otherEntity)

        if isinstance(otherEntity, Player) and self.iFrames <= 0:
            if otherEntity.dmgTimer <= 0:
                self.handle_collision_with_player(otherEntity)

    def update(self, dt):
        self.playerRef = self.manager.playerRef
        self.repulsion(dt)
        self.movement(self.playerRef.rect, dt)
        if self.iFrames > 0:
            self.iFrames -= dt
        if self.stunTimer > 0:
            self.stunTimer -= dt

        super().update(dt)
        self.boundEnemy()

        self.sprite.update(dt)

    def repulsion(self, dt):
        # REPULSION
        repulsionForce = 10
        distThreshold = self.rect[2]*0.5
        for enemy in self.manager.enemies:
            distVec = subtract(self.rect, enemy.rect)
            mag = magnitude(distVec)
            if mag < distThreshold and mag != 0:
                self.forces = add(self.forces, scalMult(distVec, repulsionForce/mag))

    def die(self):
        print("Die was not overriden by child!")

class EnemyManager(Entity):
    def __init__(self, gameRef):
        self.enemies = []
        self.toRemove = []
        super().__init__("EnemyManager", [0,0,0,0], "Manager", gameRef)
        
        self.update_refs()
    
    def update_refs(self):
        try:
            self.enemyManagerRef = self.game.curr_world.entities["Manager"]["EnemyManager"]
            self.coinManagerRef = self.game.curr_world.entities["Manager"]["CoinManager"]
            self.shopManagerRef = self.game.curr_world.entities["Manager"]["ShopManager"]
            self.particleManagerRef = self.game.curr_world.entities["Manager"]["ParticleManager"]
            self.playerRef = self.game.curr_world.entities["Player"]["player"]

        except AttributeError as e: # if world isnt initialized yet
            print("world not ready")
            self.enemyManagerRef = None
            self.coinManagerRef = None
            self.shopManagerRef = None
            self.playerRef = None
            self.particleManagerRef = None

    def spawnEnemy(self, enemyType, pos):
        self.enemies.append(enemyType(pos, self.game, self))
        self.game.curr_world.add_entity(self.enemies[len(self.enemies)-1])

    def remove(self, enemy):
        self.toRemove.append(enemy)

    def update(self, dt):
        self.update_refs()
        for enemy in self.enemies:
            enemy.update(dt)

        for enemy in self.toRemove:
            self.enemies.remove(enemy)
            self.game.curr_world.delete_entity(enemy)
        self.toRemove = []

    def draw(self, window):
        for enemy in self.enemies:
            enemy.draw(window)

class Fly(Enemy):
    def __init__(self, pos, gameRef, manager):
        rect = [pos[0], pos[1], 60, 60]
        super().__init__(rect, "fly", gameRef)

        self.speed = 8
        self.gravity = 0

        self.health = 20
        self.contactDmg = 5
        self.contactKnockback = 10

        self.stunTimer = 0
        self.stunTime = 0.8

        self.iFrames = 0
        self.iFramesMax = 0.4
        self.value = 10

        self.manager = manager
        self.sprite = Spritesheet(self.rect, "assets/fly_sprite_sheet.png", [32,32], 0)
        self.sprite.addState("idle", 0, 6)

    def die(self):
        coinDrop = round(random.randint(2,10) * self.playerRef.lootMultiplier)
        self.manager.coinManagerRef.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,coinDrop)
        self.manager.particleManagerRef.bloodExplosion(self.rect[0], self.rect[1])
        self.manager.remove(self)

    def draw(self, window):
        self.sprite.draw(self.rect, window)

    def movement(self, playerRect, dt):
        if self.stunTimer <= 0:
            moveDir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
            magnitude = math.sqrt(moveDir[0]**2 + moveDir[1]**2)
            if magnitude != 0:
                moveSpeed = self.speed/magnitude
                self.forces[0] += moveSpeed * moveDir[0]
                self.forces[1] += moveSpeed * moveDir[1]

