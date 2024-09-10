import sys
import os

sys.path.append(os.path.abspath("lib"))
sys.path.append(os.path.abspath("src"))

from library import *
from world import *
from scene import *

from enemies import *
from coinManager import *
from shopManager import *
from player import *
from particles import *
from ui import *
from waves import *

NGARU = True
escC = False
esc = False

boostResetCap = 0
menu = Menu() 

# def Game and Scenes #
game = Game()

# entities #
player = Player(W/2, H/2, game)

particleManager = ParticleManager(game)
coinManager = CoinManager(game)
shopManager = shopManager(game)
enemyManager = EnemyManager(game)

waveManager = WaveManager(game)
# -------- #

startingEntities = []
startingEntities.append(player)
startingEntities.append(particleManager)
startingEntities.append(coinManager)
startingEntities.append(shopManager)
startingEntities.append(enemyManager)

startingEntities.append(waveManager)

collisionRules = {
    "Player": ["Enemy", "Coin"],
    "Enemy": ["Player", "Bullet"],
    "Bullet": ["Bullet"],
    "Manager":[],
    "Particle":[],
    "Coin":["Player"]
}
print(startingEntities)
mainScene = Scene("main", startingEntities, collisionRules, game)
game.add_scene(mainScene)
game.switch_scenes("main")
# ------------------- #
def update(window, dt):
    '''
    global keys, mouse, boostResetCap

    menu.update(keys)
    if menu.open == False:
        if waveManager.swapVal == 1: # if not in store or transitioning from store
            if boostResetCap == 1 and player.boostState == True:
                player.dmghold = player.dmg
                player.atshold = player.attackRate
                player.spdhold = player.speed
                boostResetCap = 0
            
            player.update(window, dt, keys, player, W, H)
        coinManager.update(dt, player)
        waveManager.update(dt, mouse)
        
        particleManager.update(dt)
        enemyManager.update(dt)
    '''
    game.update(dt)

    #input stuff
    game.mouse.update()
    game.keys = pygame.key.get_pressed()
    game.camera.update(dt)

bgCol = (80,80,80)

def draw(window, dt):
    drawRect(window, (-W/2, -H/2, W*2, H*2), bgCol)
    '''
    particleManager.draw(window, dt)
    player.draw(window, player, dt)
    coinManager.draw(window)
    enemyManager.draw(window)
    waveManager.draw(dt, window)
    
    player.choiceDesc(window)
    player.statShow(window, W)

    if menu.open:
        menu.draw(window, player)
    '''
    game.draw(window)

maxFPS = 60
clock = pygame.time.Clock()

def main():
    window = init(W, H, "Untitled Roguelike")
    running = True

    while running:  # main game loop
        dt = clock.tick(maxFPS) / 1000.0

        update(window, dt)
        draw(window, dt)

        running = menu.quit

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    print("Done")


if __name__ == "__main__":
    main()
