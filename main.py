from library import *
from enemies import *
from coinManager import *
from shopManager import *
from player import *

W = 1600
H = 900
keys = [0] * 512  #init keys to avoid index error (pygame has 512 keycodes)
# to access the state of a key (true for down false for up) use "keys[pygame.KEYCODE]"
# eg) if keys[pygame.KEY_a]:
#         print("a down")


player = Player(W/2, H/2)
enemiesOnScreen = []
coinManager = CoinManager()
shopManager = shopManager(W, H)
spawnTimer = 0
waveTimer = 60

def Espawn(sc, dt, etype):
    global waveTimer
    if waveTimer > 0:
        global spawnTimer
        for i in range(1):
            if spawnTimer <= 0:
                spawnTimer = sc
                spawnLoc = random.randint(0,3)
                match spawnLoc:
                    case 0: # left
                        enemiesOnScreen.append(etype(-player.rect[2],random.randint(0,H-player.rect[3])))
                    case 1: # right
                        enemiesOnScreen.append(etype(W+player.rect[2],random.randint(0,H-player.rect[3])))
                    case 2: # up
                        enemiesOnScreen.append(etype(random.randint(0,W-player.rect[3]), -player.rect[3]))
                    case 3: # down
                        enemiesOnScreen.append(etype(random.randint(0,W-player.rect[3]), H+player.rect[3]))
            
            else:
                spawnTimer -= dt
                waveTimer -= dt
                print(waveTimer)

def update(window, dt):
    global keys, spawnRate, spawnTimer, enemiesOnScreen
    player.update(window, dt, keys)
    coinManager.update(dt, player)
    
    for enemy in enemiesOnScreen:
        enemy.update(window,player,dt,enemiesOnScreen,coinManager);

    shopManager.update(dt)
    Espawn(1, dt, BasicEnemy)

    keys = pygame.key.get_pressed()

def draw(window, dt):
    drawRect(window, (0, 0, W, H), (50, 50, 50))
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
