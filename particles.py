from library import *


class Blood:
    def __init__(self, x, y):
        self.size = 10
        self.w = 10
        self.h = 10
        self.x = x
        self.y = y
        self.col = (random.randint(100,255),0,0)
        theta = math.atan2(random.randint(-360,360)/360, random.randint(-360,360)/360)
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

class Blue:
    def __init__(self, x, y):
        self.size = 20
        self.w = self.size
        self.h = self.size
        self.x = x - 10
        self.y = y - 10
        self.col = (0,0,255)
        theta = math.atan2(random.randint(-360,360)/360, random.randint(-360,360)/360)
        self.velx = math.cos(theta)*random.uniform(500,1000)
        self.vely = math.sin(theta)*random.uniform(500,1000)
        
        math.sin(1)

    def update(self,particlesOnScreen,dt):
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
        
            

    def draw(self,window):
            drawRect(window,(self.x,self.y,self.w,self.h),self.col)

class Splash:
    def __init__(self, x, y):
        self.size = 20
        self.w = self.size
        self.h = self.size
        self.x = x
        self.y = y
        self.velx = random.randint(-200,200)
        self.vely = random.randint(-1000,-10)
        self.col = (0,0,255)
        
        math.sin(1)

    def update(self,particlesOnScreen,dt):
        self.x += self.velx * dt #X pos + vel
        self.y += self.vely * dt #Y pos + vel
        self.velx *= 0.8 #X friction
        self.vely *= 0.8 #Y friction

        if self.size <= 0:
            particlesOnScreen.remove(self)
        else:
            self.size -= 30 * dt
            self.x += 30 * dt
            self.y += 30 * dt
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