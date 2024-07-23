from library import *


class Blood:
    def __init__(self, x, y):
        self.size = 10
        self.w = 10
        self.h = 10
        self.x = x
        self.y = y
        self.col = (random.randint(100,255),0,0)
        theta = math.atan2(random.uniform(-1,1), random.uniform(-1,1))
        self.velx = math.cos(theta)*random.uniform(500,1000)
        self.vely = math.sin(theta)*random.uniform(500,1000)

    def update(self,particlesOnScreen,dt):
        self.x += self.velx * dt #X pos + vel
        self.y += self.vely * dt #Y pos + vel
        self.velx *= 0.9 #X friction
        self.vely *= 0.9 #Y friction

        if self.size <= 0:
            particlesOnScreen.remove(self)
        else:
            self.size -= 40 * dt
            self.x += 40 * dt
            self.y += 40 * dt
        self.w = self.size
        self.h = self.size
            

    def draw(self,window):
            drawRect(window,(self.x,self.y,self.w,self.h),self.col)

class Fire:
    def __init__(self, x, y):
        self.size = 20
        self.w = self.size
        self.h = self.size
        self.x = x - 10
        self.y = y - 10
        self.col = [255,random.uniform(0,50),0]
        theta = math.atan2(random.uniform(-1,-1),random.uniform(-0.3,0.3))
        self.velx = math.cos(theta) *random.uniform(50,400)
        self.vely = math.sin(theta) *random.uniform(50,300) #random.uniform(500,1000)
        

    def update(self,particlesOnScreen,dt):
        if AABBCollision((-30, -30, 1980, 30),(self.x,self.y,self.w,self.h)) and self.vely < 0:
            self.vely *= -1
        if AABBCollision((-30, 1080, 1980, 30),(self.x,self.y,self.w,self.h)) and self.vely > 0:
            self.vely *= -1
        if AABBCollision((-30, -30, 30, 1080),(self.x,self.y,self.w,self.h)) and self.velx < 0:
            self.velx *= -1
        if AABBCollision((1920, -30, 30, 1080),(self.x,self.y,self.w,self.h)) and self.velx > 0:
            self.velx *= -1
        self.x += self.velx * dt #X pos + vel
        self.y += self.vely * dt #Y pos + vel
        self.velx *= 0.98 #X friction
        self.vely *= 0.98 #Y friction

        if self.size <= 0:
            particlesOnScreen.remove(self)
        else:
            self.size -= 40 * dt
            self.y += 20 * dt
            self.x += 20 * dt
        if self.col[1] <= 180:
            self.col[1] += 600 * dt
        self.w = self.size
        self.h = self.size
        
            

    def draw(self,window):
            drawRect(window,(self.x,self.y,self.w,self.h),(self.col))

class Splash:
    def __init__(self, x, y):
        self.size = 20
        self.w = self.size
        self.h = self.size
        self.x = x - 10
        self.y = y - 10
        self.col = (0,0,255)
        theta = math.atan2(random.uniform(-1,1), random.uniform(-1,1))
        self.velx = math.cos(theta)*random.uniform(500,1000)
        self.vely = math.sin(theta)*random.uniform(500,1000)
        

    def update(self,particlesOnScreen,dt):
        if AABBCollision((-30, -30, 1980, 30),(self.x,self.y,self.w,self.h)) and self.vely < 0:
            self.vely *= -1
        if AABBCollision((-30, 1080, 1980, 30),(self.x,self.y,self.w,self.h)) and self.vely > 0:
            self.vely *= -1
        if AABBCollision((-30, -30, 30, 1080),(self.x,self.y,self.w,self.h)) and self.velx < 0:
            self.velx *= -1
        if AABBCollision((1920, -30, 30, 1080),(self.x,self.y,self.w,self.h)) and self.velx > 0:
            self.velx *= -1
        self.x += self.velx * dt #X pos + vel
        self.y += self.vely * dt #Y pos + vel
        self.velx *= 0.98 #X friction
        self.vely *= 0.98 #Y friction

        if self.size <= 0:
            particlesOnScreen.remove(self)
        else:
            self.size -= 40 * dt
            self.x += 40 * dt
            self.y += 40 * dt
        self.w = self.size
        self.h = self.size
        
    #if self.velx > 0 and self.velx <= 0.1:
        #    particlesOnScreen.remove(self)
        #elif self.velx < 0 and self.velx >= 0-.1:
        #    particlesOnScreen.remove(self)
        #elif self.vely > 0 and self.vely <= 0.1:
        #    particlesOnScreen.remove(self)
        #elif self.vely < 0 and self.vely >= -0.1:
        #    particlesOnScreen.remove(self)

    def draw(self,window):
            drawRect(window,(self.x,self.y,self.w,self.h),self.col)