from library import *

class Bullet:
    def __init__(self,bx,by,v):
        w, h = 20, 20
        self.r = w / 2
        self.rect = [bx,by,h,w]
        self.vel = v
    def update(self,dt, player):
        mag = magnitude(self.vel)
        if mag > player.bulletSpeed:
            self.vel = scalMult(self.vel, player.bulletSpeed/mag)
        self.rect[0] += self.vel[0] * dt
        self.rect[1] += self.vel[1] * dt
    def draw(self,window):
        drawCircle(window, ((self.rect[0]+self.r, self.rect[1]+self.r), self.r), (255,255,255))
        

class Player:
    def __init__(self, x, y):
        w, h = 40, 40
        self.r = w / 2
        self.rect = [x, y, w, h]  # position = self.rect[0], self.rect[1]
        self.center = [x+w/2,y+h/2]
        self.col = (127, 35, 219)
        self.vel = [0, 0]
        self.speed = 2500
        self.mhealth = 100
        self.health = self.mhealth
        self.bullets = []
        self.dmgTimer = 0
        self.ac = 0
        self.attackRate = 0.35
        self.dmg = 5
        self.coins = 1000000
        self.inaccuracy = 0.13
        self.bulletSpeed = 500
        self.itemQty = {}
        self.homing = 0

    def homingSpeed(self):
        self.homing += 1
        self.bulletSpeed /= 2
        self.dmg *= 0.8

    def accuracyUp(self):
        self.inaccuracy -= 0.02

    def speedUp(self):
        self.speed += 500
        print(self.speed)

    def atkSpeedUp(self):
        self.attackRate *= 0.9 # have to do this otherwise u get 0 firerate really quickly
        print(self.attackRate)

    def dmgUp(self):
        self.dmg += 2
        print(self.dmg)

    def healthUp(self):
        self.health += 20

    def bulletSpeedUp(self):
        self.bulletSpeed += 100

    def triggerCardFunc(self,name):
        if name in self.itemQty.keys():
            self.itemQty[name] += 1
            print(self.itemQty[name])
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

    def takeDmg(self, dmgAmount, dmgKnockback = [0,0], enemy = False):

        if self.dmgTimer <= 0:
            if enemy:
                enemy.vel = scalMult(dmgKnockback, -1)
            self.health -= dmgAmount
            self.vel = add(self.vel, dmgKnockback)
            self.dmgTimer = 2
            print("ouch!")
            print(f"health: {self.health}")

    def physics(self, dt):
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.center = [self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2]
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9

    def input(self, dt, keys):
        # movement
        dir = [0, 0]
        if keys[pygame.K_w]:
            dir[1] += -1
        if keys[pygame.K_s]:
            dir[1] += 1
        if keys[pygame.K_a]:
            dir[0] += -1
        if keys[pygame.K_d]:
            dir[0] += 1
        SF = math.sqrt(dir[0]**2 + dir[1]**2)
        if SF != 0:
            self.vel[0] += self.speed * dt * dir[0] / SF
            self.vel[1] += self.speed * dt * dir[1] / SF
        
        # shooting
        dis = subtract(pygame.mouse.get_pos(), self.rect)
        dx = dis[0]
        dy = dis[1]
        if self.inaccuracy < 0:
            inac = 0
        else:
            inac = random.uniform(1 * self.inaccuracy,-1 * self.inaccuracy)

        theta = math.atan2(dy, dx) + inac
        bv = [0,0]
        bv[0] = math.cos(theta)*self.bulletSpeed
        bv[1] = math.sin(theta)*self.bulletSpeed
        self.ac -= 1 * dt
        if pygame.mouse.get_pressed(num_buttons=3)[0] and self.ac < 0:
            self.bullets.append(Bullet(self.rect[0]+self.rect[2]/4,self.rect[1]+self.rect[3]/4,bv))
            self.ac = self.attackRate
        # [x, y]
        
        # theta = math.atan2(mousey-playery, mousex-playerx))

        # find theta then find vec (cos theta, sin theta)
        # Bullet(self,x,y,vel)
        # vel = bullet speed * vec
        # self.bullets.append(Bullet(self.rect[0],self.rect[1],vel))

        #hp bar
        
    

    def update(self, window, dt, keys):
        self.input(dt, keys)
        self.physics(dt)
        for bullet in self.bullets:
            bullet.update(dt, self)
        if self.dmgTimer > 0:
            self.dmgTimer -= dt

    def draw(self, window):
        drawText(window, f"Coins: {self.coins}", (255,255,0), (10,50), 40)
        drawText(window, f"HP: {self.health}", (0,255,0), (10,10), 40)
        if self.dmgTimer > 0:
            if math.floor(self.dmgTimer*10) % 2 != 0:
                drawCircle(window, (self.center, self.r), self.col)
        else:
            drawCircle(window, (self.center, self.r), self.col)
            
        ratio = self.health / self.mhealth
        healthBarPos = [160, 18.5]
        pygame.draw.rect(window, (255, 0, 0), (*healthBarPos, 200, 20))
        pygame.draw.rect(window, (0, 255, 0), (*healthBarPos, 200 * ratio, 20))
        for bullet in self.bullets:
            bullet.draw(window)
