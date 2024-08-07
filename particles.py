from library import *

class ParticleManager:
    def __init__(self):
        self.particles = []
        self.toRemove = []

    def remove(self, particle):
        self.toRemove.append(particle)

    def spawnFire(self, x, y):
        numOfParticles = 2
        for i in range(numOfParticles):
            theta = random.uniform(0, 1)*-math.pi
            vel = [math.cos(theta)*random.uniform(50,200), math.sin(theta)*random.uniform(50,300)]
            size = random.randint(4,15)

            randomMax = 255
            randomHalf = 128
            randomMin = 0
            startingColor = (randomMax,randomMax,randomMax,255) # white -> yellow -> orange -> red -> smoke
            lerpColors = [(randomMax,randomMax,randomMin,255), (randomMax,randomHalf,randomMin,255), (randomMax,randomMin,randomMin,255), (randomHalf,randomHalf,randomHalf,255)]
            
            self.particles.append(Particle(self, [x, y, size, size], startingColor, vel, colorLerp=lerpColors, grav=-20, lifetime=0.5+random.uniform(0,1.4)))

    def bloodExplosion(self, x, y):
        for i in range(20):
            col = (random.randint(100,255),0,0, 255) #(R, G, B, A)
            theta = math.atan2(random.uniform(-1,1), random.uniform(-1,1))
            velx = math.cos(theta)*random.uniform(100,1000)
            vely = math.sin(theta)*random.uniform(100,1000)
            size = random.randint(1,12)

            self.particles.append(Particle(self, [x,y,size,size], col, [velx, vely], lifetime=10, fade=True, grav=0))

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)

        for particle in self.toRemove:
            try:
                self.particles.remove(particle)
            except ValueError:
                print("ValueError when removing particles!")
        self.toRemove = []

    def draw(self, window, dt):
        for particle in self.particles:
            particle.draw(window, dt)

class Particle:
    def __init__(self, manager, rect, col=(0,0,0,255), vel=[0,0], drag=0.9, grav=10, shrink=False, fade=True, colorLerp=False, lifetime=10): # col = (R, G, B, A)
        self.rect = rect
        self.color = col
        self.vel = vel
        self.drag = drag
        self.gravity = grav

        self.lifetime = lifetime
        self.shrink = shrink
        self.fade = fade
        self.colorLerp = colorLerp

        self.startingLifetime = lifetime

        self.manager = manager

        if self.colorLerp:
            self.currentColor = self.color
            self.numOfColors = 1+len(self.colorLerp)
            self.colorThreshhold = 1/self.numOfColors
            self.currentColorIndex = 1
            self.subLerp = 1

    def draw(self, window, dt):
        displayRect = self.rect
        scalingFactor = self.lifetime/self.startingLifetime

        if self.shrink:
            displayRect = [displayRect[0], displayRect[1], displayRect[2]*scalingFactor, displayRect[3]*scalingFactor]

        if self.fade:
            self.color = (self.color[0], self.color[1], self.color[2], 255*self.lifetime/self.startingLifetime)

        if self.colorLerp:
            if self.subLerp > 0:
                self.subLerp -= dt/self.colorThreshhold
                self.color = (lerp(self.color[0], self.colorLerp[self.currentColorIndex-1][0], 0.1), lerp(self.color[1], self.colorLerp[self.currentColorIndex-1][1], 0.1), lerp(self.color[2], self.colorLerp[self.currentColorIndex-1][2], 0.1), self.color[3])


            else:
                if self.currentColorIndex < self.numOfColors-1:
                    self.currentColorIndex += 1
                self.subLerp = 1

        col = pygame.Color(self.color)
        drawRect(window, displayRect, col)

    def update(self, dt):
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt

        self.vel[1] += self.gravity

        self.vel = scalMult(self.vel, self.drag)

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.manager.remove(self)
