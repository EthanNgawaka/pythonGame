from library import *
from player import *
from particles import *

class Enemy:
    def __init__(self):
        pass
        
    def draw(self, window):
        print("Draw was not overriden by child!")

    def physics(self, dt):
        self.movement(self.playerRef.rect, dt)

        fric = 0.98
        accel = [self.forces[0]*self.invMass,self.forces[1]*self.invMass]
        self.vel[0] += accel[0]*dt
        self.vel[1] += accel[1]*dt
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel = [self.vel[0]*fric,self.vel[1]*fric]
        self.forces = [0,0]

        self.boundEnemy()

    def boundEnemy(self):
        leftCheck = self.rect[0] < -self.rect[2] and self.vel[0] < 0
        rightCheck = self.rect[0] > W+self.rect[2] and self.vel[0] > 0
        if leftCheck or rightCheck:
            self.vel[0] *= -1

        upCheck = self.rect[1] < -self.rect[3] and self.vel[1] < 0
        downCheck = self.rect[1] > H+self.rect[3] and self.vel[1] > 0
        if upCheck or downCheck:
            self.vel[1] *= -1    

    def checkBulletCollision(self, bullet):
        distVec = subtract(self.rect, bullet.rect)
        mag = magnitude(distVec)
        
        # if bulletHoming then make it home in
        if mag < self.playerRef.homing*150:
            bullet.vel = add(bullet.vel, scalMult(distVec, self.playerRef.bulletSpeed/(4*mag)))
        if AABBCollision(self.rect,(self.playerRef.mace.x, self.playerRef.mace.y, 40, 40)):
            self.iFrames = self.iFramesMax

            if mag != 0:
                self.vel = scalMult(distVec, self.playerRef.knockback/mag)
                self.stunTimer = self.stunTime
            
            if self.playerRef.health < self.playerRef.maxHealth:
                self.playerRef.health += self.playerRef.lifeSteal
                if self.playerRef.health > self.playerRef.maxHealth:
                    self.playerRef.health = self.playerRef.maxHealth

            if bullet.pierces <= 0:
                self.playerRef.bullets.remove(bullet)
            else:
                self.playerRef.pierces -= 1

            if self.health <= 0:
                self.die()
                return True

            return False

        check = AABBCollision(self.rect,bullet.rect)
        if check:
            if bullet.type == "haloBullet":
                self.health -= self.playerRef.dmg*self.playerRef.dmgMultiplier*4
            else:
                self.health -= self.playerRef.dmg*self.playerRef.dmgMultiplier
            self.iFrames = self.iFramesMax

            if mag != 0:
                self.vel = scalMult(distVec, self.playerRef.knockback/mag)
                self.stunTimer = self.stunTime
            
            if self.playerRef.health < self.playerRef.maxHealth:
                self.playerRef.health += self.playerRef.lifeSteal
                if self.playerRef.health > self.playerRef.maxHealth:
                    self.playerRef.health = self.playerRef.maxHealth

            if bullet.pierces <= 0:
                self.playerRef.bullets.remove(bullet)
            else:
                self.playerRef.pierces -= 1

            if self.health <= 0:
                self.die()
                return True

            return False

    def shadow(self):
        print("Child didnt override shadow()!")

    def update(self, dt):
        self.physics(dt)
        self.collisions(dt)
        self.sprite.update(dt)
        self.shadow()

    def collisions(self, dt):
        collisionCheck = AABBCollision(self.rect, self.playerRef.rect)

        # player contact dmg collisions
        if collisionCheck:
            knockbackVec = scalMult(collisionCheck, self.contactKnockback/magnitude(collisionCheck))
            self.playerRef.takeDmg(self.contactDmg, scalMult(knockbackVec, -1), self)

        if self.iFrames <= 0:
            for bullet in self.playerRef.bullets:
                if self.checkBulletCollision(bullet):
                    break # if enemy dies
        self.iFrames -= dt

        # REPULSION
        repulsionForce = 5000
        distThreshold = self.rect[2]
        for enemy in self.manager.enemies:
            distVec = subtract(self.rect, enemy.rect)
            mag = magnitude(distVec)
            if mag < distThreshold and mag != 0:
                self.forces = add(self.forces, scalMult(distVec, repulsionForce/mag))

    def die(self):
        print("Die was not overriden by child!")

class EnemyManager:
    def __init__(self, coinManager, player, particleManager):
        self.enemies = []
        self.toRemove = []

        self.coinManagerRef = coinManager
        self.playerRef = player
        self.particleManagerRef = particleManager
    
    def spawnEnemy(self, enemyType, pos):
        self.enemies.append(enemyType(pos, self.coinManagerRef, self.playerRef, self.particleManagerRef, self))

    def remove(self, enemy):
        self.toRemove.append(enemy)

    def update(self, dt):
        for enemy in self.enemies:
            enemy.update(dt)
        for enemy in self.toRemove:
            self.enemies.remove(enemy)
        self.toRemove = []

    def draw(self, window):
        for enemy in self.enemies:
            enemy.draw(window)

class Fly(Enemy):
    def __init__(self, pos, coinManager, player, particleManager, enemyManager):
        self.rect = [pos[0], pos[1], 60, 60]

        self.vel = [0,0]
        self.speed = 800
        self.forces = [0,0]
        self.invMass = 1

        self.health = 20
        self.contactDmg = 5
        self.contactKnockback = 200

        self.stunTimer = 0
        self.stunTime = 0.1

        self.iFrames = 0
        self.iFramesMax = 0.1
        self.value = 10

        self.coinManagerRef = coinManager
        self.playerRef = player
        self.particleManagerRef = particleManager
        self.manager = enemyManager
        self.sprite = Spritesheet(self.rect, "assets/fly_sprite_sheet.png", [32,32], 0)
        self.sprite.addState("idle", 0, 6)

    def shadow(self):
        shadowManager.addShadowToRender(add(getRectCenter(self.rect), [-self.rect[2]/20,self.rect[3]/4]), self.rect[3]/4, (50,0,50,128)) # shadow

    def die(self):
        coinDrop = round(random.randint(2,10) * self.playerRef.lootMultiplier)
        self.coinManagerRef.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,coinDrop)
        self.particleManagerRef.bloodExplosion(self.rect[0], self.rect[1])
        self.manager.remove(self)

    def draw(self, window):
        self.sprite.draw(self.rect, window)

    def movement(self, playerRect, dt):
        if self.stunTimer > 0:
            self.stunTimer -= dt
        else:
            dir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
            magnitude = math.sqrt(dir[0]**2 + dir[1]**2)
            if magnitude != 0:
                moveSpeed = self.speed/magnitude
                self.forces[0] += moveSpeed * dir[0]
                self.forces[1] += moveSpeed * dir[1]

# VVVVVVVVVVV      REIMPLIMENT THESE TWO       VVVVVVVVVVVVV

class InvisEnemy:
    def __init__(self, x, y):
        self.rect = [x,y,30,30]
        self.r = self.rect[2]/2
        self.col = (0,0,255)
        self.vel = [0,0]
        self.speed = 400
        self.health = 40
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
        self.vis = True
        
    def draw(self, window):
        if self.health > 0 and self.vis == True:
            drawCircle(window,((self.rect[0]+self.r,self.rect[1]+self.r),self.r),self.col)
            if self.health < 10:
                mlep = 8
            else:
                mlep = 0
            drawText(window, f"{round(self.health)}", (255,255,255),(self.rect[0] + mlep, self.rect[1] - 5), 30)

    def update(self, window, player, dt, enemiesOnScreen, coinManager, particleManager):
        self.dmgKnockback = player.knockback
        if self.health > 0:
            if self.tickCount > 0:
                if self.tDTimer < 0:
                    self.health -= player.hotShotDmg
                    # FIRE
                    self.colchan = 0.1
                    self.tickCount -= 1
                    self.tDTimer = self.tDTimerMax
                    if self.health <= 0:
                                coinDrop = round(random.randint(2,10) * player.lootMultiplier)
                                coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,coinDrop)
                                enemiesOnScreen.remove(self)
                                # BLOOD
                                particleManager.bloodExplosion(self.rect[0], self.rect[1])
                else:
                    self.tDTimer -= dt
                    if self.colchan > 0:
                        self.col = (255,69,0)
                        self.colchan -= dt
                    else:
                        self.col = (255,0,0)
            self.trackPlayer(player.rect, dt)
            self.physics(dt)
            self.collisions(player, enemiesOnScreen, coinManager, dt, particleManager)

    def collisions(self, player, enemiesOnScreen, coinManager, dt, particleManager):
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
                                # BLOOD
                                particleManager.bloodExplosion(self.rect[0], self.rect[1])
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
                                # BLOOD
                                particleManager.bloodExplosion(self.rect[0], self.rect[1])
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
        fric = 0.9
        accel = [self.forces[0]*self.invMass,self.forces[1]*self.invMass]
        self.vel[0] += accel[0]*dt
        self.vel[1] += accel[1]*dt
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel = [self.vel[0]*fric,self.vel[1]*fric]
        self.forces = [0,0]
        if AABBCollision((-30, -30, 1980, 30),self.rect) and self.vel[1] < 0:
            self.vel[1] *= -1
        if AABBCollision((-30, 1080, 1980, 30),self.rect) and self.vel[1] > 0:
            self.vel[1] *= -1
        if AABBCollision((-30, -30, 30, 1080),self.rect) and self.vel[0] < 0:
            self.vel[0] *= -1
        if AABBCollision((1920, -30, 30, 1080),self.rect) and self.vel[0] > 0:
            self.vel[0] *= -1

    def trackPlayer(self, playerRect, dt):
        if self.stunTimer > 0:
            self.stunTimer -= dt
        else:
            dir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
            magnitude = math.sqrt(dir[0]**2 + dir[1]**2)
            if magnitude < 200 and magnitude > 100:
                self.vel = [0,0]
            if magnitude < 100:
                self.vis = True
            else:
                self.vis = False
                
            if magnitude != 0:
                moveSpeed = self.speed/magnitude
                self.forces[0] += moveSpeed * dir[0]
                self.forces[1] += moveSpeed * dir[1]

	
class DasherEnemy:
    def __init__(self, x, y):
        self.rect = [x,y,30,30]
        self.r = self.rect[2]/2
        self.col = (0,0,255)
        self.vel = [0,0]
        self.speed = 800
        self.health = 10
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
        self.vis = True
        self.dashcool = 1
        
    def draw(self, window):
        if self.health > 0 and self.vis == True:
            drawCircle(window,((self.rect[0]+self.r,self.rect[1]+self.r),self.r),self.col)
            if self.health < 10:
                mlep = 8
            else:
                mlep = 0
            drawText(window, f"{round(self.health)}", (255,255,255),(self.rect[0] + mlep, self.rect[1] - 5), 30)

    def update(self, window, player, dt, enemiesOnScreen, coinManager, particleManager):
        self.dmgKnockback = player.knockback
        if self.health > 0:
            if self.tickCount > 0:
                if self.tDTimer < 0:
                    self.health -= player.hotShotDmg
                    # FIRE PARTICLES

                    self.colchan = 0.1
                    self.tickCount -= 1
                    self.tDTimer = self.tDTimerMax
                    if self.health <= 0:
                                coinDrop = round(random.randint(2,10) * player.lootMultiplier)
                                coinManager.spawnCoin(self.rect[0]+self.rect[2]/2, self.rect[1]+self.rect[3]/2,coinDrop)
                                enemiesOnScreen.remove(self)
                                for i in range(20):
                                    # BLOOD PARTICLES
                                    particleManager.bloodExplosion(self.rect[0], self.rect[1])
                else:
                    self.tDTimer -= dt
                    if self.colchan > 0:
                        self.col = (255,69,0)
                        self.colchan -= dt
                    else:
                        self.col = (255,0,0)
            self.trackPlayer(player.rect, dt)
            self.physics(dt)
            self.collisions(player, enemiesOnScreen, coinManager, dt, particleManager)

    def collisions(self, player, enemiesOnScreen, coinManager, dt, particleManager):
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
                                # BLOOD
                                particleManager.bloodExplosion(self.rect[0], self.rect[1])
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
                                # BLOOD
                                particleManager.bloodExplosion(self.rect[0], self.rect[1])
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
        fric = 0.9
        accel = [self.forces[0]*self.invMass,self.forces[1]*self.invMass]
        self.vel[0] += accel[0]*dt
        self.vel[1] += accel[1]*dt
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel = [self.vel[0]*fric,self.vel[1]*fric]
        self.forces = [0,0]
        if AABBCollision((-30, -30, 1980, 30),self.rect) and self.vel[1] < 0:
            self.vel[1] *= -1
        if AABBCollision((-30, 1080, 1980, 30),self.rect) and self.vel[1] > 0:
            self.vel[1] *= -1
        if AABBCollision((-30, -30, 30, 1080),self.rect) and self.vel[0] < 0:
            self.vel[0] *= -1
        if AABBCollision((1920, -30, 30, 1080),self.rect) and self.vel[0] > 0:
            self.vel[0] *= -1
    def trackPlayer(self, playerRect, dt):
        if self.stunTimer > 0:
            self.stunTimer -= dt
        else:
            if self.dashcool <= 0:
                dirINX = (random.randint(0,100) -50)
                dirINY = (random.randint(0,100) -50)
                dir = [playerRect[0] - self.rect[0] + dirINX, playerRect[1] - self.rect[1] + dirINY]
                self.speed = 20000
                self.dashcool = random.randint(0,4) * 0.5
            else:
                self.speed = 800
                dir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
                self.dashcool -= dt
            magnitude = math.sqrt(dir[0]**2 + dir[1]**2)
            if magnitude != 0:
                moveSpeed = self.speed/magnitude
                self.forces[0] += moveSpeed * dir[0]
                self.forces[1] += moveSpeed * dir[1]
