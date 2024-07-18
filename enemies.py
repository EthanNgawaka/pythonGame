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
        self.stunTime = 0.1
        self.iFrames = 0
        self.iFramesMax = 0.1
        self.tDTimerMax = 1
        self.tDTimer = 0
        self.colchan = 0
        self.tickCount = 0
        
    def draw(self, window):
        if self.health > 0:
            drawCircle(window,((self.rect[0]+self.r,self.rect[1]+self.r),self.r),self.col)
            if self.health < 10:
                mlep = 8
            else:
                mlep = 0
            drawText(window, f"{round(self.health)}", (255,255,255),(self.rect[0] + mlep, self.rect[1] - 5), 30, drawAsUI=True)

    def update(self, window, player, dt, enemiesOnScreen, coinManager):
        self.dmgKnockback = player.knockback
        if self.health > 0:
            if self.tickCount > 0:
                if self.tDTimer < 0:
                    self.health -= player.hotShotDmg
                    self.colchan = 0.1
                    self.tickCount -= 1
                    self.tDTimer = self.tDTimerMax
                    if self.health <= 0:
                                coinDrop = round(random.randint(2,10) * player.lootMultiplier)
                                coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,coinDrop)
                                enemiesOnScreen.remove(self)
                else:
                    self.tDTimer -= dt
                    if self.colchan > 0:
                        self.col = (255,69,0)
                        self.colchan -= dt
                    else:
                        self.col = (255,0,0)
            self.trackPlayer(player.rect, dt)
            self.physics(dt)
            self.collisions(player, enemiesOnScreen, coinManager, dt)

    def collisions(self, player, enemiesOnScreen, coinManager, dt):
        collisionCheck = AABBCollision(self.rect, player.rect)
        if collisionCheck:
            knockbackVec = scalMult(collisionCheck, self.contactKnockback/magnitude(collisionCheck))
            player.takeDmg(self.contactDmg, scalMult(knockbackVec, -1), self)

        if self.iFrames <= 0:
            match player.weapon:
                case "gun":
                    for bullet in player.bullets:
                        distVec = subtract(self.rect, bullet.rect)
                        mag = magnitude(distVec)
                        if mag < player.homing*150:
                            bullet.vel = add(bullet.vel, scalMult(distVec, player.bulletSpeed/(4*mag)))
                        check = AABBCollision(self.rect,bullet.rect)
                        if check:
                            if bullet.type == "haloBullet":
                                self.health -= player.dmg*player.dmgMultiplier*4
                            else:
                                self.health -= player.dmg*player.dmgMultiplier
                            self.iFrames = self.iFramesMax

                            if mag != 0:
                                self.vel = scalMult(distVec, self.dmgKnockback/mag)
                                self.stunTimer = self.stunTime

                            if player.hotShotDmg > 0:
                                self.tickCount += 5
                            
                            if player.health < player.maxHealth:
                                player.health += player.lifeSteal
                            if bullet.pierces <= 0:
                                player.bullets.remove(bullet)
                            else:
                                bullet.pierces -= 1
                            if self.health <= 0:
                                coinDrop = round(random.randint(2,10) * player.lootMultiplier)
                                coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,coinDrop)
                                enemiesOnScreen.remove(self)
                                break
                case "sword": 
                    for i in player.sword.swordsegments:
                        distVec = subtract(self.rect, i)
                        mag = magnitude(distVec)
                        check = AABBCollision(self.rect,i)
                        if check:
                            self.health -= player.dmg*player.dmgMultiplier
                            self.iFrames = self.iFramesMax
                            

                            if mag != 0:
                                self.vel = scalMult(distVec, self.dmgKnockback/mag)
                                self.stunTimer = self.stunTime

                            if self.health <= 0:
                                coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,random.randint(2,10))
                                enemiesOnScreen.remove(self)
                                break

        player.sword.swordsegments = []
        self.iFrames -= dt

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

	
