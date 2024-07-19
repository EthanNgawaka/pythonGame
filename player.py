from library import *
from enemies import *

class Bullet:
    def __init__(self,bx,by,v,dmg,pierces,bulletType="standardBullet"):
        w, h = dmg, dmg
        self.r = w / 2
        self.rect = [bx,by,h,w]
        self.vel = v
        self.type = bulletType
        self.haloDistMax = 150
        self.haloDist = 0
        self.theta = 0
        self.pierces = pierces

    def update(self,dt, player):
        mag = magnitude(self.vel)
        if mag > player.bulletSpeed:
            self.vel = scalMult(self.vel, player.bulletSpeed/mag)

        match self.type:
            case "standardBullet":
                self.rect[0] += self.vel[0] * dt
                self.rect[1] += self.vel[1] * dt
                if AABBCollision((-50, -50, 2020, 5),self.rect) and self.vel[1] < 0:
                    player.bullets.remove(self)
                elif AABBCollision((-50, 1080+45, 2020, 5),self.rect) and self.vel[1] > 0:
                    player.bullets.remove(self)
                elif AABBCollision((-50, -50, 5, 1180),self.rect) and self.vel[0] < 0:
                    player.bullets.remove(self)
                elif AABBCollision((1920+45, -50, 5, 1180),self.rect) and self.vel[0] > 0:
                    player.bullets.remove(self)

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
        self.coins = 0
        self.foragerval = 0
        self.lootMultiplier = 1
        self.itemQty = {}
        self.actives = {"Space":None, "E":None, "Q":None} # "Key": [Cooldown, Timer, ActiveFunc, name, text offset]
        self.cooldownReduct = 0
        self.boostState = False
        self.boostTime = 0
        self.dmghold = 0
        self.spdhold = 0
        self.atshold = 0
        self.pierces = 0
        self.lifeSteal = 0
        self.hotShotDmg = 0
        self.revives = 0
        self.invinceTimer = 0
        self.revCol = [255,255,255]
        self.atkMSav = 1
        self.choicehovering = "none"
        self.running = True
        

    
    def statShow(self, window, W):
        drawText(window, f"Speed: {round(self.speed/500,3)}", (255,255,255),(10, 150), 30, drawAsUI=True)
        drawText(window, f"Dmg: {round(self.dmg,3)}", (255,255,255),(10, 200), 30, drawAsUI=True)
        drawText(window, f"Acc: {round(self.inaccuracy,3)}", (255,255,255),(10, 250), 30, drawAsUI=True)
        drawText(window, f"BSpeed: {round(self.bulletSpeed/10,1)}", (255,255,255),(10, 300), 30, drawAsUI=True)
        drawText(window, f"AtkSpeed: {round(self.attackRate,3)}", (255,255,255,1),(10, 350), 30, drawAsUI=True)
        drawText(window, f"AtkSpeedMult: {round(self.atkRateMultiplier,3)}", (255,255,255),(10, 400), 30, drawAsUI=True)
        
        #drawText(window, self.choicehovering, (255,255,255),(10, 450), 30, drawAsUI=True)
        
        


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
            
    def buyBoost(self):
        if self.boostState == False: #sketchy setup ask ethan how to remove card from pool when bought *
            self.boostState = True
            for index in self.actives:
                if not self.actives[index]:
                    self.dmghold = self.dmg
                    self.atshold = self.attackRate
                    self.spdhold = self.speed
                    self.actives[index] = [10, 0, self.boost, "Boost", 20]
                    return
            
                

    def dash(self, dt):
        SF = magnitude(self.dir)
        if SF != 0:
            self.vel[0] += 100000 * dt * self.dir[0] / SF
            self.vel[1] += 100000 * dt * self.dir[1] / SF

    def bulletHalo(self, dt):
        for i in range(0,8):
            self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, [i,0], self.getBulletSize(self.dmg*2.5)[0],self.pierces, "haloBullet"))

    def boost(self, dt):
        self.dmghold = self.dmg
        self.atshold = self.attackRate
        self.spdhold = self.speed
        self.boostTime = 5

    def hotShot(self):
        self.hotShotDmg += 1

    def lifeStealUp(self):
        self.lifeSteal += 1

    # passive items
    def doubleShot(self):
        self.bulletCount += 1
        self.accuracyUp()

    def minigun(self):
        self.dmgMultiplier = 0.2
        self.inaccuracy += 0.1
        self.speedinac += 50
        self.atkRateMultiplier = 5
        self.atkMSav = 5
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
        self.maxHealth += 20

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
        self.cooldownReduct += 5

    def piercing(self):
        self.pierces += 1

    def lifeUp(self):
        self.revives += 1
    
    def getBulletSize(self, dmg=0):
        if dmg == 0:
            dmg = self.dmg
        return [max(self.minBlltSize, self.dmgMultiplier*(dmg+2)*2)]*2
    
    def buySword(self):
        self.weapon = "sword"
        self.knockback = 400
        self.atkRateMultiplier = 1.1
        self.atkMSav = 1.1
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
            case "shieldUp":
                self.shield()
            case "activecooldown":
                self.activeCooldown()
            case "piercing":
                self.piercing()
            case "lifeStealUp":
                self.lifeStealUp()
            case "hotShotUp":
                self.hotShot()
            case "pheonix":
                self.lifeUp()

            # actives
            case "halo":
                self.buyBulletHalo()
            case "dash":
                self.buyDash()
            case "boost":
                self.buyBoost()
            case "sword":
                self.buySword()

    def takeDmg(self, dmgAmount, dmgKnockback = [0,0], enemy = False):
        
        if self.dmgTimer <= 0 and self.invinceTimer <= 0:
            if enemy:
                enemy.vel = scalMult(dmgKnockback, -1)
            if self.shieldCur <= 0:
                self.health -= dmgAmount
            else:
                self.shieldCur -= 1
            self.vel = add(self.vel, dmgKnockback)
            self.dmgTimer = 2
            if self.health <= 0 and self.revives > 0:
                self.health = self.maxHealth
                self.invinceTimer = 3
            elif self.health <= 0:
                self.running = False
            

    def physics(self, dt, W, H):
        if AABBCollision((0, 0, W, 5),self.rect) and self.vel[1] < 0:
            self.vel[1] *= -0.25
        if AABBCollision((0, H-5, W, 5),self.rect) and self.vel[1] > 0:
            self.vel[1] *= -0.25
        if AABBCollision((0, 0, 5, H),self.rect) and self.vel[0] < 0:
            self.vel[0] *= -0.25
        if AABBCollision((W-5, 0, 5, H),self.rect) and self.vel[0] > 0:
            self.vel[0] *= -0.25
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.center = [self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2]
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9
        

    def input(self, dt, keys, window, player, W, H):
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
                        
                        self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4, self.rect[1]+self.rect[3]/4, bv, self.getBulletSize()[0],self.pierces))
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
                    activeObj[1] = activeObj[0] * (1 - (self.cooldownReduct/100))
    def boostReset(self, dt):
        if self.boostTime > 0:
            self.dmg = self.dmghold * 1.5
            self.attackRate = self.atshold /3
            self.speed = self.spdhold* 3
            self.boostTime -= dt
            self.col = (255,0,0)
        else:
            self.dmg = self.dmghold
            self.attackRate = self.atshold
            self.speed = self.spdhold
            self.col = (127, 35, 219)
    
    def getDescription(self):
        tDesc = 0
        desc = ["ERROR","increases how fast the player moves", "Increases bullet damage", "Increases the players firerate", "Increases how much health the player has", "Increases how fast a bullet traves", "Reduces active cooldowns", "Increases accuracy","Lots of bullets but not much damage", "gain the ability to dash", "Shoot a ring of bullets", "Increases gold gain", "Increases enemy spawnrate", "Increases shield level", "Increases firerate, damage and speed for a short period", "Bullets pierce through enemies", "When you hit an enemy gain health", "Set our enemy on fire", "Come back from the dead"]
        desc2 = ["ERROR","+1 speed","+2 damage","+10% attack rate","+20 max health","+1 bullet speed","-5% active cooldowns","-0.02 innacuracy","+3 bullets, /2 damage", "+1 dash ability", "+1 halo ability", "1.5x gold (+0.25 every level)", "-0.2s enemy spawn time", "+1 shield", "+boost ability", "+1 pierces", "+1 lifeSteal", "+1 burn damage", "+1 revive"]
        ["shotgun", "dash", "halo", "forager", "fighter", "shieldUp", "boost", "piercing", "lifeStealUp", "hotShotUp", "pheonix"]
        desc3 = ["ERROR","","","","","",""]
        if self.choicehovering == "speedUp":
            tDesc = 1
        elif self.choicehovering == "dmgUp":
            tDesc = 2
        elif self.choicehovering == "atkSpeedUp":
            tDesc = 3
        elif self.choicehovering == "healthUp":
            tDesc = 4
        elif self.choicehovering == "bulletSpeed":
            tDesc = 5
        elif self.choicehovering == "activecooldown":
            tDesc = 6
        elif self.choicehovering == "accuracyUp":
            tDesc = 7
        elif self.choicehovering == "shotgun":
            tDesc = 8
        elif self.choicehovering == "dash":
            tDesc = 9
        elif self.choicehovering == "halo":
            tDesc = 10
        elif self.choicehovering == "forager":
            tDesc = 11
        elif self.choicehovering == "fighter":
            tDesc = 12
        elif self.choicehovering == "shieldUp":
            tDesc = 13
        elif self.choicehovering == "boost":
            tDesc = 14
        elif self.choicehovering == "piercing":
            tDesc = 15
        elif self.choicehovering == "lifeStealUp":
            tDesc = 16
        elif self.choicehovering == "hotShotUp":
            tDesc = 17
        elif self.choicehovering == "pheonix":
            tDesc = 18
        return desc[tDesc], desc2,tDesc

    def choiceDesc(self,window):
        if self.choicehovering != "none":
            
            description, desc2, dn = self.getDescription()
            d2 = desc2[dn]
            mx, my = pygame.mouse.get_pos()
            drawRect(window,(mx,my,500,250),(150,150,150))
            drawText(window, self.choicehovering, (0,0,0),(mx + 10,my), 30, drawAsUI=True)
            drawText(window, description, (0,0,0),(mx + 10,my + 50), 30, drawAsUI=True)
            drawText(window, d2, (0,0,0),(mx + 10,my + 75), 30, drawAsUI=True)
            drawText(window, description, (0,0,0),(mx + 10,my + 50), 30, drawAsUI=True)
            
        

    def update(self, window, dt, keys, player, W ,H):
        self.input(dt, keys, window, player, W, H)
        self.physics(dt, W, H)
        if self.boostState == True:
            self.boostReset(dt)
        if self.invinceTimer <= 0:
            self.col = (127, 35, 219)
            self.reCol = [255,255,255]
            self.atkRateMultiplier = self.atkMSav
        else:
            self.invinceTimer -= dt
            self.revCol[0] -= dt * ((255 - 127)/5)
            self.revCol[1] -= dt * ((255 - 35)/5)
            self.revCol[2] -= dt * ((255 - 219)/5)
            self.col = (self.revCol)
            self.atkRateMultiplier = self.atkMSav * 2

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
        if self.invinceTimer > 0:
            drawText(window, f"{round(self.invinceTimer)}", (100,100,100),(self.rect[0] + 12.5, self.rect[1]), 30, drawAsUI=True)

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

        
