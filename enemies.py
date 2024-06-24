from library import *
from player import *


class BasicEnemy:
    def __init__(self, x, y):
        self.rect = [x,y,30,30]
        self.r = self.rect[2]/2
        self.col = (255,0,0)
        self.vel = [0,0]
        self.speed = 800
        self.health = 20
        self.forces = [0,0]
        self.invMass = 1
        self.contactDmg = 5
        self.contactKnockback = 200
        self.stunTimer = 0
        self.stunTime = 0.5
        self.iSec = 1
        
    def draw(self, window):
        if self.health > 0:
            drawCircle(window,((self.rect[0]+self.r,self.rect[1]+self.r),self.r),self.col)

    def update(self, window, player, dt, enemiesOnScreen, coinManager, sword):
        self.dmgKnockback = player.knockback
        if self.health > 0:
            self.trackPlayer(player.rect, dt)
            self.physics(dt)
            self.collisions(player, enemiesOnScreen, coinManager, sword, dt)

    def collisions(self, player, enemiesOnScreen, coinManager, sword, dt):
        collisionCheck = AABBCollision(self.rect, player.rect)
        if collisionCheck:
            knockbackVec = scalMult(collisionCheck, self.contactKnockback/magnitude(collisionCheck))
            player.takeDmg(self.contactDmg, scalMult(knockbackVec, -1), self)

        if self.iSec <= 0:
            for bullet in player.bullets:
                distVec = subtract(self.rect, bullet.rect)
                mag = magnitude(distVec)
                if mag < player.homing*150:
                    bullet.vel = add(bullet.vel, scalMult(distVec, player.bulletSpeed/(4*mag)))
                check = AABBCollision(self.rect,bullet.rect)
                if check:
                    self.health -= player.dmg*player.dmgMultiplier
                    self.iSec = 2

                    if mag != 0:
                        self.vel = scalMult(distVec, self.dmgKnockback/mag)
                        self.stunTimer = self.stunTime

                    player.bullets.remove(bullet)
                    if self.health <= 0:
                        coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,random.randint(2,10))
                        enemiesOnScreen.remove(self)
                        break
            
            for i in sword.swordsegments:
                distVec = subtract(self.rect, i)
                mag = magnitude(distVec)
                check = AABBCollision(self.rect,i)
                if check:
                    self.health -= player.dmg*player.dmgMultiplier
                    self.iSec = 2
                    print("hit!")
                    

                    if mag != 0:
                        self.vel = scalMult(distVec, self.dmgKnockback/mag)
                        self.stunTimer = self.stunTime

                    if self.health <= 0:
                        coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,random.randint(2,10))
                        enemiesOnScreen.remove(self)
                        break
            sword.swordsegments = []
        self.iSec -= dt

        repulsionForce = 5000
        distThreshold = self.rect[2]
        for enemy in enemiesOnScreen:
            distVec = subtract(self.rect, enemy.rect)
            mag = magnitude(distVec)
            if mag < distThreshold and mag != 0:
                self.forces = add(self.forces, scalMult(distVec, repulsionForce/mag))

    def physics(self, dt):
        fric = 0.98
        accel = [self.forces[0]*self.invMass,self.forces[1]*self.invMass]
        self.vel[0] += accel[0]*dt
        self.vel[1] += accel[1]*dt
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel = [self.vel[0]*fric,self.vel[1]*fric]
        self.forces = [0,0]

    def trackPlayer(self, playerRect, dt):
        if self.stunTimer > 0:
            self.stunTimer -= dt
        else:
            dir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
            magnitude = math.sqrt(dir[0]**2 + dir[1]**2)
            if magnitude != 0:
                moveSpeed = self.speed/magnitude
                self.forces[0] += moveSpeed * dir[0]
                self.forces[1] += moveSpeed * dir[1]

	
