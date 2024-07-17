from library import *
from enemies import *

class Bullet:
    def __init__(self,bx,by,v,dmg,bulletType="standardBullet"):
        w, h = dmg, dmg
        self.r = w / 2
        self.rect = [bx,by,h,w]
        self.vel = v
        self.type = bulletType
        self.haloDistMax = 150
        self.haloDist = 0
        self.theta = 0

    def update(self,dt, player):
        mag = magnitude(self.vel)
        if mag > player.bulletSpeed:
            self.vel = scalMult(self.vel, player.bulletSpeed/mag)

        match self.type:
            case "standardBullet":
                self.rect[0] += self.vel[0] * dt
                self.rect[1] += self.vel[1] * dt

            case "haloBullet": # using vel[0] for index of bullet
                if self.haloDist < self.haloDistMax:
                    self.haloDist += 200 * dt
                
                phi = self.vel[0]*math.pi/4 + self.theta
                self.rect = [player.center[0]-self.r/2+self.haloDist*math.cos(phi), player.center[1]-self.r/2+self.haloDist*math.sin(phi),self.rect[2],self.rect[3]]

                self.theta += dt * (math.pi)

            case "orbitBullet":
                pass

        # tiny planet scraps
        #elif player.weapon == 3:
            #self.rect[0] = player.center[0] + self.vel[0]
            #self.rect[1] = player.center[1] + self.vel[1]
    def draw(self,window):
        drawCircle(window, ((self.rect[0]+self.r, self.rect[1]+self.r), self.r), (255,255,255))

class Sword:
    def __init__(self):
        self.swing = False
        self.swlength = 60
        self.swangle = 1.5
        self.swcool = 20
        self.swordrect = [0,0,10,10]
        self.swc = 1
        self.swordsegments = []

    def draw(self,window,player):
            center = player.center
            mousePos = pygame.mouse.get_pos()
            dx, dy = subtract(mousePos, center)
            theta = math.atan2(dy, dx) + player.sword.swangle
            sx, sy = 0,0
            index = player.sword.swlength
            for i in range(player.sword.swlength):
                sx = center[0] + math.cos(theta) * (index)
                sy = center[1] + math.sin(theta) * (index)
                self.swordsegments.append((sx,sy,10,10))
                index += 1
                drawCircle(window, ((sx,sy), 5), (255,255,255))


class Player:
    def __init__(self, x, y):

# physics, consts, timers, and  rect stuff
        w, h = 40, 40
        self.r = w / 2
        self.rect = [x, y, w, h]  # position = self.rect[0], self.rect[1]
        self.center = [x+w/2,y+h/2] 
        self.col = (127, 35, 219)
        self.vel = [0, 0]
        self.dir = [0, 0]
        self.weapon = "gun"

        self.minBlltSize = 9
        self.atkTimer = 0 # attack timer
        self.dmgTimer = 0

        self.activeKeys = [pygame.K_SPACE, pygame.K_e, pygame.K_q]

# player properties
    # movement and health
        self.speed = 2500
        self.maxHealth = 100 #max health
        self.health = self.maxHealth
    # dmg and firerate stuff
        self.dmgMultiplier = 1
        self.atkRateMultiplier = 1
        self.dmg = 5
        self.homing = 0
        self.bdir = [0,0]
        self.dmginc = 2
    # bullet stuff
        self.speedinac = 0
        self.attackRate = 0.35
        self.bulletCount = 1
        self.bullets = []
        self.inaccuracy = 0.13
        self.bulletSpeed = 500
        self.knockback = 100
    # misc
        self.sword = Sword()
        self.shieldMax = 0
        self.shieldCur = 0
        self.spawnMultiplyer = 0
        self.coins = 1000000
        self.foragerval = 0
        self.lootMultiplier = 1
        self.itemQty = {}
        self.actives = {"Space":None, "E":None, "Q":None} # "Key": [Cooldown, Timer, ActiveFunc, name, text offset]
        self.cooldownReduct = 10

        
        

    
    def statShow(self, window, W):
        drawText(window, f"Speed: {self.speed/500}", (255,255,255),(10, 150), 30, drawAsUI=True)
        drawText(window, f"Dmg: {self.dmg}", (255,255,255),(10, 200), 30, drawAsUI=True)
        drawText(window, f"Acc: {self.inaccuracy}", (255,255,255),(10, 250), 30, drawAsUI=True)
        drawText(window, f"BSpeed: {self.bulletSpeed/500}", (255,255,255),(10, 300), 30, drawAsUI=True)
        if self.actives["Space"]:
            drawText(window, f"cool1: {self.actives["Space"][0]}", (255,255,255),(10, 350), 30, drawAsUI=True)
        
        


    # active items
    def buyBulletHalo(self):
        for index in self.actives:
            if not self.actives[index]:
                self.actives[index] = [15, 0, self.bulletHalo, "Halo", 26]
                return

    def buyDash(self):
        for index in self.actives:
            if not self.actives[index]:
                self.actives[index] = [1.5, 0, self.dash, "Dash", 20]
                return

    def dash(self, dt):
        SF = magnitude(self.dir)
        if SF != 0:
            self.vel[0] += 100000 * dt * self.dir[0] / SF
            self.vel[1] += 100000 * dt * self.dir[1] / SF

    def bulletHalo(self, dt):
        for i in range(0,8):
            self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, [i,0], self.getBulletSize(self.dmg*2.5)[0], "haloBullet"))

    # passive items
    def doubleShot(self):
        self.bulletCount += 1
        self.accuracyUp()

    def minigun(self):
        self.dmgMultiplier = 0.2
        self.inaccuracy += 0.1
        self.speedinac += 50
        self.atkRateMultiplier = 5
        self.bulletSpeed += 500

    def homingSpeed(self):
        self.homing += 1
        self.bulletSpeed /= 2
        self.dmg *= 0.8

    def accuracyUp(self):
        self.inaccuracy -= 0.02

    def speedUp(self):
        self.speed += 500

    def atkSpeedUp(self):
        self.attackRate *= 0.9 # have to do this otherwise u get 0 firerate really quickly

    def dmgUp(self):
        self.dmg += self.dmginc

    def healthUp(self):
        self.health += 20

    def bulletSpeedUp(self):
        self.bulletSpeed += 100

    def shotgun(self):
        self.bulletCount += 3
        self.dmg /= 2
        self.inaccuracy += 0.1
        self.speedinac += 50
        self.attackRate += 0.1

    def fighter(self):
        self.spawnMultiplyer += 1
        
    def shield(self):
        self.shieldMax += 1

    def activeCooldown(self):
        for index in self.actives:
            if self.actives[index]:
                self.actives[index][0] = (self.actives[index][0]/100) *95
                self.cooldownReduct += 5
        return

    
    def getBulletSize(self, dmg=0):
        if dmg == 0:
            dmg = self.dmg
        return [max(self.minBlltSize, self.dmgMultiplier*(dmg+2)*2)]*2
    
    def buySword(self):
        self.weapon = 2
        self.knockback = 400
        self.atkRateMultiplier = 1.1
        self.dmg *= 0.1
        self.dmginc = 0.1
    
    def forager(self):
        self.foragerval += 1

    def triggerCardFunc(self,name):
        if name in self.itemQty.keys():
            self.itemQty[name] += 1
        else:
            self.itemQty[name] = 1
        match name:

            #passives
            case "speedUp":
                self.speedUp()
            case "atkSpeedUp":
                self.atkSpeedUp()
            case "dmgUp":
                self.dmgUp()
            case "healthUp":
                self.healthUp()
            case "bulletSpeed": 
                self.bulletSpeedUp()
            case "accuracyUp":
                self.accuracyUp()
            case "homingSpeed":
                self.homingSpeed()
            case "shotgun":
                self.shotgun()
            case "minigun":
                self.minigun()
            case "doubleShot":
                self.doubleShot()
            case "forager":
                self.forager()
            case "fighter":
                self.fighter()
            case "shield":
                self.shield()
            case "activecooldown":
                self.activeCooldown()

            # actives
            case "halo":
                self.buyBulletHalo()
            case "dash":
                self.buyDash()
            #case "sword":
            #    self.buySword()

    def takeDmg(self, dmgAmount, dmgKnockback = [0,0], enemy = False):

        if self.dmgTimer <= 0:
            if enemy:
                enemy.vel = scalMult(dmgKnockback, -1)
            if self.shieldCur <= 0:
                self.health -= dmgAmount
            else:
                self.shieldCur -= 1
            self.vel = add(self.vel, dmgKnockback)
            self.dmgTimer = 2

    def physics(self, dt):
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.center = [self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2]
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9
        

    def input(self, dt, keys, window, player):
        # movement
        self.dir = [0, 0]
        if keys[pygame.K_w]:
            self.dir[1] += -1
        if keys[pygame.K_s]:
            self.dir[1] += 1
        if keys[pygame.K_a]:
            self.dir[0] += -1
        if keys[pygame.K_d]:
            self.dir[0] += 1

        SF = magnitude(self.dir)
        if SF != 0:
            self.vel[0] += self.speed * dt * self.dir[0] / SF
            self.vel[1] += self.speed * dt * self.dir[1] / SF
        
        # shooting
        bulletRect = self.getBulletSize()
        mousePos = pygame.mouse.get_pos()
        dis = subtract(mousePos, self.center)
        dx = dis[0]
        dy = dis[1]
        
        self.atkTimer -= dt
        if pygame.mouse.get_pressed(num_buttons=3)[0] and self.atkTimer < 0:
            match self.weapon:
                case "gun":
                    for i in range(self.bulletCount):
                        if self.inaccuracy < 0:
                            inac = 0
                        else:
                            inac = random.uniform(1 * self.inaccuracy,-1 * self.inaccuracy)
                        theta = math.atan2(dy, dx) + inac
                        bv = [0,0]
                        bv[0] = math.cos(theta)*self.bulletSpeed + random.uniform(self.speedinac,-self.speedinac)
                        bv[1] = math.sin(theta)*self.bulletSpeed + random.uniform(self.speedinac,-self.speedinac)
                        
                        self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, bv, self.getBulletSize()[0]))
                        self.atkTimer = self.attackRate/self.atkRateMultiplier
                
                case "sword":
                    if self.sword.swing == False:
                        self.sword.swing = True
                        self.atkTimer = self.attackRate/self.atkRateMultiplier

            # scraps of ngarus tiny planet implimentation
            #elif self.weapon == 3:
                #for i in range(self.bulletCount):
                    #theta = math.atan2(dy, dx)
                    #bv = [0,0]
                    #bv[0] = math.cos(theta)* 100
                    #bv[1] = math.sin(theta)* 100
                    #
                    #self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, bv, self.getBulletSize()[0]))
                    #self.atkTimer = self.attackRate/self.atkRateMultiplier
            #elif self.weapon == 4:
                #for i in range(self.bulletCount):
                    #if self.inaccuracy < 0:
                        #inac = 0
                    #else:
                        #inac = random.uniform(1 * self.inaccuracy,-1 * self.inaccuracy)
                    #mousePos = pygame.mouse.get_pos()
                    #dis = subtract(mousePos, self.center)
                    #dx = dis[0]
                    #dy = dis[1]
                    #theta = math.atan2(dy, dx)
                    #bv = [theta + inac,1]
                    #
                    #self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, bv, self.getBulletSize()[0]))
                    #self.atkTimer = self.attackRate/self.atkRateMultiplier
                    
                    

        #ijkl controlls (this is for the steam deck/ if they want to use 8 directional shooting instead if mouse)
        #elif self.ctrl == True:
            #self.bdir = [0, 0]
            #if keys[pygame.K_i]:
                #self.bdir[1] += -1
            #if keys[pygame.K_k]:
                #self.bdir[1] += 1
            #if keys[pygame.K_j]:
                #self.bdir[0] += -1
            #if keys[pygame.K_l]:
                #self.bdir[0] += 1
            #if self.bdir != [0,0] and self.atkTimer < 0:
                #for i in range(self.bulletCount):
                    #if self.inaccuracy < 0:
                        #inac = 0
                    #else:
                        #inac = random.uniform(1 * self.inaccuracy,-1 * self.inaccuracy)
                    #bv = [0,0]
                    #bv[0] = self.bdir[0]*self.bulletSpeed + random.uniform(self.speedinac,-self.speedinac)
                    #bv[1] = self.bdir[1]*self.bulletSpeed + random.uniform(self.speedinac,-self.speedinac)
                    #
                    #self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, bv, self.getBulletSize()[0]))
                    #self.atkTimer = self.attackRate/self.atkRateMultiplier



        # "Key": [Cooldown, Timer, ActiveFunc]
        for i in range(len(self.actives)):
            activeObj = self.actives[list(self.actives.keys())[i]]
            if activeObj != None:
                if activeObj[1] >= 0:
                    activeObj[1] -= dt
                elif keys[self.activeKeys[i]]:
                    activeObj[2](dt)
                    activeObj[1] = activeObj[0]

    def update(self, window, dt, keys, player):
        self.input(dt, keys, window, player)
        self.physics(dt)


        for bullet in self.bullets:
            bullet.update(dt, self)

        if self.dmgTimer > 0:
            self.dmgTimer -= dt
        if self.foragerval <= 1:
            self.lootMultiplier = 1.25 + (0.25 * self.foragerval)

            
    def draw(self, window, player, dt):
        drawText(window, f"Coins: {self.coins}", (255,255,0), (10,50), 40, drawAsUI=True)
        drawText(window, f"HP: {self.health}", (0,255,0), (10,10), 40, drawAsUI=True)
        if self.dmgTimer > 0:
            if math.floor(self.dmgTimer*10) % 2 != 0:
                drawCircle(window, (self.center, self.r), self.col)
        else:
            drawCircle(window, (self.center, self.r), self.col)
            
        ratio = self.health / self.maxHealth
        healthBarPos = [160, 18.5]
        pygame.draw.rect(window, (255, 0, 0), (*healthBarPos, 200, 20))
        pygame.draw.rect(window, (0, 255, 0), (*healthBarPos, 200 * ratio, 20))

        # Weapons
        for bullet in self.bullets:
            bullet.draw(window)
        if self.sword.swing == True and self.sword.swangle >= -1.5:
                self.sword.draw(window,player)
                self.sword.swangle -= 0.2
                if self.sword.swangle <= -1.5:
                    self.sword.swangle = 1.5
                    self.sword.swing = False

        # Actives
        # "Key": [Cooldown, Timer, ActiveFunc]
        for i in range(len(self.actives)):
            activeObj = self.actives[list(self.actives.keys())[i]]
            # draw card for active

        
