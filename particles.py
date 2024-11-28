from game import *

def scalMult(vec, scal):
    return [vec[0]*scal, vec[1]*scal]
# so i just ripped the old particle system and changed like 2 lines to work with the new engine lol
def spawn_fire(x, y):
    numOfParticles = 2
    for i in range(numOfParticles):
        theta = random.uniform(0, 1)*-math.pi
        vel = pygame.Vector2(math.cos(theta)*random.uniform(50,200), math.sin(theta)*random.uniform(50,300))
        size = random.randint(4,15)

        randomMax = 255
        randomHalf = 80
        randomMin = 0
        startingColor = (randomMax,randomMax,randomMax,255) # white -> yellow -> orange -> red -> smoke
        lerpColors = [(randomMax,randomMax,randomMin,255), (randomMax,randomHalf,randomMin,255), (randomMax,randomMin,randomMin,255), (randomHalf,randomHalf,randomHalf,255)]
        
        part = Particle(Rect((x-size/2, y-size/2), (size, size)), vel, random.uniform(0.5,1.9), lerpColors)
        part.color = startingColor
        part.gravity = -20
        game.curr_scene.add_entity(part, "particle_fire", 2)

def spawn_acid_particle(x, y):
    numOfParticles = 3
    for i in range(numOfParticles):
        theta = random.uniform(-1, 1)*-math.pi
        vel = pygame.Vector2(math.cos(theta)*random.uniform(50,200), math.sin(theta)*random.uniform(50,300))
        size = random.randint(4,15)

        randomMax = 255
        randomHalf = 90
        randomMin = 0
        startingColor = (randomMin,randomMax,randomMin,255) # white -> yellow -> orange -> red -> smoke
        lerpColors = [(randomMin,randomHalf,randomMin,255), (randomMin,randomHalf,randomMin,255), (randomHalf,randomHalf,randomHalf,255)]
        
        part = Particle(Rect((x-size/2, y-size/2), (size, size)), vel, random.uniform(0.5,1.9), lerpColors)
        part.color = startingColor
        part.gravity = -10
        game.curr_scene.add_entity(part, "particle_fire", 2)

def spawn_weakness_particle(x, y):
    numOfParticles = 3
    for i in range(numOfParticles):
        theta = random.uniform(-1, 1)*-math.pi
        vel = pygame.Vector2(math.cos(theta)*random.uniform(50,200), math.sin(theta)*random.uniform(50,300))
        size = random.randint(4,15)

        randomMax = 255
        randomHalf = 80
        randomMin = 0
        startingColor = (randomHalf,randomHalf,randomHalf,255) # white -> yellow -> orange -> red -> smoke
        lerpColors = [(randomHalf,randomHalf,randomMin,255), (randomMin,randomMin,randomMin,255), (randomHalf,randomHalf,randomHalf,255)]
        
        part = Particle(Rect((x-size/2, y-size/2), (size, size)), vel, random.uniform(0.5,1.9), lerpColors)
        part.color = startingColor
        part.gravity = -10
        game.curr_scene.add_entity(part, "particle_fire", 2)

# TODO redo this cause it wont work???
def blood_explosion(x, y, amnt, init_theta=None):
    numOfParticles = round(max(amnt, 5))
    for i in range(numOfParticles):
        theta = random.uniform(-math.pi, math.pi)
        # improve this i want it to be normall distrubted with
        # mu = init_theta and std dev idk
        if init_theta is not None:
            theta /= 4
            theta += init_theta
        mag = random.uniform(0,1000)
        vel = pygame.Vector2(math.cos(theta)*mag, math.sin(theta)*mag)
        size = max(3,random.uniform(numOfParticles/2, numOfParticles))

        startingColor = (random.randint(128, 255),0,0,255) # white -> yellow -> orange -> red -> smoke
        
        part = Particle(Rect((x-size/2, y-size/2), (size, size)), vel, random.uniform(5,15))
        part.color = startingColor
        part.gravity = 0

        parts = game.get_entities_by_id("particle")
        game.curr_scene.add_entity(part, "particle_blood", 2)

class Particle(Entity):
    def __init__(self, rect, vel, lifetime, colorLerp = False): # col = (R, G, B, A)
        self.rect = rect
        self.color = (255,255,255)
        self.vel = vel
        self.drag = 0.9
        self.gravity = 10

        self.startingLifetime = lifetime
        self.lifetime = self.startingLifetime
        self.shrink = False
        self.fade = True
        self.colorLerp = colorLerp


        if self.colorLerp:
            self.currentColor = self.color
            self.numOfColors = 1+len(self.colorLerp)
            self.colorThreshhold = 1/self.numOfColors
            self.currentColorIndex = 1
            self.subLerp = 1

    def draw(self, window):
        displayRect = self.rect
        scalingFactor = self.lifetime/self.startingLifetime

        if self.shrink:
            displayRect = [displayRect[0], displayRect[1], displayRect[2]*scalingFactor, displayRect[3]*scalingFactor]

        if self.fade:
            self.color = (self.color[0], self.color[1], self.color[2], 255*self.lifetime/self.startingLifetime)

        if self.colorLerp:
            if self.subLerp > 0:
                self.color = (lerp(self.color[0], self.colorLerp[self.currentColorIndex-1][0], 0.1), lerp(self.color[1], self.colorLerp[self.currentColorIndex-1][1], 0.1), lerp(self.color[2], self.colorLerp[self.currentColorIndex-1][2], 0.1), self.color[3])


            else:
                if self.currentColorIndex < self.numOfColors-1:
                    self.currentColorIndex += 1
                self.subLerp = 1

        col = pygame.Color(self.color)
        drawRect(window, displayRect, col)

    def update(self, dt):
        if self.colorLerp:
            if self.subLerp > 0:
                self.subLerp -= dt/self.colorThreshhold

        self.rect.x += self.vel[0]*dt
        self.rect.y += self.vel[1]*dt

        if game.time_speed >= 1:
            self.vel.y += self.gravity
            self.vel *= self.drag

        self.lifetime -= dt
        if self.lifetime <= 0:
            self.remove_self()

