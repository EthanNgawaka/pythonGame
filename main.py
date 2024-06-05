from library import *
from enemies import *

W = 800
H = 600
keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")

class Bullet:
    def __init__(self,bx,by,v):
        self.rect = [bx,by,10,10]
        self.vel = v
    def update(self,dt):
        self.rect[0] += self.vel[0] * dt
        self.rect[1] += self.vel[1] * dt
    def draw(self,window):
        drawRect(window,self.rect,(255,255,255))

class Player:
    def __init__(self, x, y):
        w, h = 40, 40
        self.r = w / 2
        self.rect = [x, y, w, h]  # position = self.rect[0], self.rect[1]
        self.center = [x+w/2,y+h/2]
        self.col = (155, 155, 155)
        self.vel = [0, 0]
        self.speed = 5000
        self.health = 100
        self.bullets = []
        self.dmgTimer = 0

    def takeDmg(self, dmgAmount, dmgKnockback = [0,0]):
        self.health -= dmgAmount
        self.vel = add(self.vel, dmgKnockback)
        self.dmgTimer = 1
        print("ouch!")
        print(f"health: {self.health}")

    def physics(self, dt):
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.center = [self.rect[0]+self.rect[2]/2,self.rect[1]+self.rect[3]/2]
        self.vel[0] *= 0.9
        self.vel[1] *= 0.9

    def input(self, dt):
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
        theta = math.atan2(dy, dx)
        bv = [0,0]
        bulletSpeed = 500
        bv[0] = math.cos(theta)*bulletSpeed
        bv[1] = math.sin(theta)*bulletSpeed
        
        if pygame.mouse.get_pressed(num_buttons=3)[0]:
            self.bullets.append(Bullet(self.rect[0],self.rect[1],bv))
        # [x, y]
        
        # theta = math.atan2(mousey-playery, mousex-playerx))

        # find theta then find vec (cos theta, sin theta)
        # Bullet(self,x,y,vel)
        # vel = bullet speed * vec
        # self.bullets.append(Bullet(self.rect[0],self.rect[1],vel))
    

    def update(self, window, dt):
        self.input(dt)
        self.physics(dt)
        for bullet in self.bullets:
            bullet.update(dt)

    def draw(self, window):
        drawCircle(window, (self.center, self.r), self.col)
        for bullet in self.bullets:
            bullet.draw(window)

player = Player(0,0)
testEnemy = BasicEnemy(110,110)


def update(window, dt):
    global keys
    player.update(window, dt)
    testEnemy.update(window, player, dt)

    keys = pygame.key.get_pressed()


def draw(window, dt):
    drawRect(window, (0, 0, W, H), (0, 0, 255))
    player.draw(window)
    testEnemy.draw(window)

maxFPS = 60
clock = pygame.time.Clock()

def main():
    window = init(W, H, "bingus 2.0")

    running = True
    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        #print(1/dt)
        update(window, dt)
        draw(window, dt)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_ESCAPE]:
            running = False

    print("Done")


if __name__ == "__main__":
    main()
