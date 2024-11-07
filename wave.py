from game import *
from enemies import *

class Wave(Entity):
    def __init__(self):
        self.enemyTypes = [
            Fly,
        ]
        self.timer = 0
        self.num = 1

        self.length = 60
        self.spawnRate = 3.5
        self.last_spawn = 0

        self.swappedAlready = False

    def update(self, dt):
        if self.timer < self.length:
            self.timer += dt

            if self.timer - self.last_spawn >= self.spawnRate:
                self.spawn_random_enemy()
                self.last_spawn = self.timer

            return
        
        copper = game.get_entities_by_type(Copper)
        enemies = game.get_entities_by_type(Enemy)
        if not self.swappedAlready and len(copper) == 0 and len(enemies) == 0:
            game.get_entity_by_id("shop").open()
            self.swappedAlready = True

    def new_round(self):
        self.timer = 0
        self.spawnRate -= 0.2
        self.last_spawn = 0
        self.num += 1
        self.swappedAlready = False
        print('new round!')

    def spawn_random_enemy(self):
        EnemyType = self.enemyTypes[random.randint(0,len(self.enemyTypes)-1)]
        w, h = 40, 40
        if random.randint(0,1) > 0:
            x = random.randint(-w,W+w)
            y = (-h if random.randint(0,1) > 0 else H+h)
        else:
            x = (-w if random.randint(0,1) > 0 else W+w)
            y = random.randint(-h,H+h)
        
        game.curr_scene.add_entity(
            EnemyType(
                pygame.Vector2(x,y), 
            ),
            "enemy" # need to change this later prob to actually use enemy type id
        )

    def draw(self, window):
        drawText(window, f"Wave Timer: {round(self.timer)}s", (0,0,0), (W-200, 200), 40, True)
        drawText(window, f"Wave #{round(self.num)}", (0,0,0), (W-200, 250), 40, True)
