from library import *
from enemies import *

class Bullet:
    def __init__(self,bx,by,v,dmg):
        w, h = dmg, dmg
        self.r = w / 2
        self.rect = [bx,by,h,w]
        self.vel = v
    def update(self,dt, player):
        mag = magnitude(self.vel)
        if mag > player.bulletSpeed:
            self.vel = scalMult(self.vel, player.bulletSpeed/mag)

        self.rect[0] += self.vel[0] * dt
        self.rect[1] += self.vel[1] * dt
        
        # tiny planet scraps
        #elif player.weapon == 3:
            #self.rect[0] = player.center[0] + self.vel[0]
            #self.rect[1] = player.center[1] + self.vel[1]
        #elif player.weapon == 4:
            #self.vel[0] += player.bulletSpeed/10000
            #bv = [0,0]
            #bv[0] = math.cos(self.vel[0])* 100
            #bv[1] = math.sin(self.vel[0])* 100
            #self.rect[0] = player.center[0] + bv[0]
            #self.rect[1] = player.center[1] + bv[1]
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
            theta = math.atan2(dy, dx) + sword.swangle
            sx, sy = 0,0
            index = sword.swlength
            for i in range(sword.swlength):
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
        self.coins = 1000000
        self.itemQty = {}
        self.actives = {"Space":None, "E":None, "Q":None} # "Key": [Cooldown, Timer, ActiveFunc]

    def buyDash(self):
        for index in self.actives:
            if not self.actives[index]:
                self.actives[index] = [2, 0, self.dash]
                return

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
    
    def dash(self, dt):
        SF = magnitude(self.dir)
        if SF != 0:
            self.vel[0] += 100000 * dt * self.dir[0] / SF
            self.vel[1] += 100000 * dt * self.dir[1] / SF

    def shotgun(self):
        self.bulletCount += 3
        self.dmg /= 2
        self.inaccuracy += 0.1
        self.speedinac += 50
        self.attackRate += 0.1

    def getBulletSize(self):
        return [max(self.minBlltSize, self.dmgMultiplier*(self.dmg+2)*2)]*2
    
    def buySword(self):
        self.weapon = 2
        self.knockback = 400
        self.atkRateMultiplier = 1.1
        self.dmg *= 0.1
        self.dmginc = 0.1
        

    def triggerCardFunc(self,name):
        if name in self.itemQty.keys():
            self.itemQty[name] += 1
        else:
            self.itemQty[name] = 1
        match name:
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
            case "Dash":
                self.buyDash()
            case "minigun":
                self.minigun()
            case "doubleShot":
                self.doubleShot()
            case "sword":
                self.buySword()

    def takeDmg(self, dmgAmount, dmgKnockback = [0,0], enemy = False):

        if self.dmgTimer <= 0:
            if enemy:
                enemy.vel = scalMult(dmgKnockback, -1)
            self.health -= dmgAmount
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
                print(activeObj[1])
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

            
    def draw(self, window, player, dt):
        drawText(window, f"Coins: {self.coins}", (255,255,0), (10,50), 40)
        drawText(window, f"HP: {self.health}", (0,255,0), (10,10), 40)
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

        
