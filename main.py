from library import *
from enemies import *
from coinManager import *
from shopManager import *

W = 1600
H = 900
keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


class Bullet:
    def __init__(self,bx,by,v):
        w, h = 20, 20
        self.r = w / 2
        self.rect = [bx,by,h,w]
        self.vel = v
    def update(self,dt):
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
        self.col = (155, 155, 155)
        self.vel = [0, 0]
        self.speed = 5000
        self.mhealth = 100
        self.health = self.mhealth
        self.bullets = []
        self.dmgTimer = 0
        self.ac = 0
        self.attackRate = 0.1
        self.dmg = 5
        self.coins = 0

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
        
    

    def update(self, window, dt):
        self.input(dt)
        self.physics(dt)
        for bullet in self.bullets:
            bullet.update(dt)
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


player = Player(W/2, H/2)
spawnRate = 999
spawnTimer = 999
enemiesOnScreen = []
coinManager = CoinManager()
shopManager = shopManager(W, H)

def update(window, dt):
    global keys, spawnRate, spawnTimer, enemiesOnScreen
    player.update(window, dt)
    coinManager.update(dt, player)
    
    if spawnTimer <= 0:
        spawnTimer = spawnRate
        spawnLoc = random.randint(0,3)
        match spawnLoc:
            case 0: # left
                enemiesOnScreen.append(BasicEnemy(-player.rect[2],random.randint(0,H-player.rect[3])))
            case 1: # right
                enemiesOnScreen.append(BasicEnemy(W+player.rect[2],random.randint(0,H-player.rect[3])))
            case 2: # up
                enemiesOnScreen.append(BasicEnemy(random.randint(0,W-player.rect[3]), -player.rect[3]))
            case 3: # down
                enemiesOnScreen.append(BasicEnemy(random.randint(0,W-player.rect[3]), H+player.rect[3]))
        
    else:
        spawnTimer -= dt

    for enemy in enemiesOnScreen:
        enemy.update(window,player,dt,enemiesOnScreen,coinManager);

    shopManager.update(dt)

    keys = pygame.key.get_pressed()

def draw(window, dt):
    drawRect(window, (0, 0, W, H), (0, 0, 255))
    player.draw(window)
    coinManager.draw(window)
    for enemy in enemiesOnScreen:
        enemy.draw(window);

    shopManager.draw(window)

maxFPS = 60
clock = pygame.time.Clock()
def main():
    window = init(W, H, "bingus 2.0")

    running = True
    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0
        update(window, dt)
        draw(window, dt)
        drawText(window, f"FPS: {1/dt}", (255,255,255),(W-150, 20), 30)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if keys[pygame.K_ESCAPE]:
            running = False

    print("Done")


if __name__ == "__main__":
    main()
