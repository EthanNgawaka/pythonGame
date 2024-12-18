from game import *
from enemies import *

class Wave(Entity):
    def __init__(self):
        self.enemyTypes = {
            "common":[Fly, Mosquito, Cockroach, Ant],
            "uncommon":[TermiteSwarm, CockroachSwarm, AntSwarm, Snail],
            "rare":[MagneticSnail, FireAntSwarm, MachinegunBug],
            "miniboss":[MotherCockroach, MotherFly],
            "boss":[],
        }
        # testing only one enemy:
        self.override_enemy_type = None

        self.timer = 0
        self.num = 1

        self.length = 60
        self.spawnRate = 3.5
        self.last_spawn = 0
        self.pause = False

        self.enemy_flags = []
        self.delayed_spawn_timer = 0

        self.swappedAlready = False
        self.miniboss_spawned = False

        self.rect = Rect((game.W - game.H*0.15, game.H*0.05), (game.H*0.1, game.H*0.1))
        self.timer_img = Spritesheet(self.rect, "./assets/timer.png", (64, 64), 0, False, (255,255,255))
        for i in range(9):
            self.timer_img.addState(f"{i}/8", i, 1)
        self.timer_img.setState("0/8")

        self.enemy_queue = [] # (enemy_args, timer)

    def update(self, dt):
        if self.pause:
            return

        for obj in self.enemy_queue:
            if obj[1] > 0:
                obj[1] -= dt
                if obj[1] < 0:
                    self.actually_spawn_enemy(*obj[0])
                    self.enemy_queue.remove(obj)

        if self.timer < self.length:
            self.timer += dt

            if self.timer - self.last_spawn >= self.spawnRate:
                wave = game.get_entity_by_id("wave")
                for i in range(random.randint(1,1+wave.num//3)):
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
        self.miniboss_spawned = False
        self.last_spawn = 0
        self.num += 1
        self.swappedAlready = False
        print('new round!')
        # reset player things here
        game.get_entity_by_id("player").new_wave()

    def actually_spawn_enemy(self,x,y,EnemyType):
        game.sfx.spawn.play()
        enemy = EnemyType(Vec2(x,y))
        # if its not instance of enemy then its a swarm type
        if isinstance(enemy, Enemy):
            game.curr_scene.add_entity(
                enemy,
                "enemy" # need to change this later prob to actually use enemy type id
            )

    def delay_spawning_enemy(self, x, y, EnemyType, delay):
        self.enemy_queue.append([[x, y, EnemyType], delay])

    def spawn_random_enemy(self):
        choice = "common"
        rand = random.uniform(0,1)
        weight = (self.num * self.timer/self.length)/4
        if rand > 0.85-0.2*weight:
            choice = "uncommon"
            rand = random.uniform(0,1)
            if rand > 0.95-0.2*weight:
                choice = "rare"

        if self.timer > self.length * 0.75 and not self.miniboss_spawned:
            choice = "miniboss"
            self.miniboss_spawned = True

        EnemyType = self.enemyTypes[choice][random.randint(0,len(self.enemyTypes[choice])-1)]
        if self.override_enemy_type is not None:
            EnemyType = self.override_enemy_type
        w, h = 40, 40
        if random.randint(0,1) > 0:
            x = random.uniform(game.W*0.1,game.W*0.9)
            y = (-h if random.randint(0,1) > 0 else game.H+h)
        else:
            x = (-w if random.randint(0,1) > 0 else game.W+w)
            y = random.uniform(game.W*0.1,game.H*0.9)

        dir = 0
        if x >= game.W:
            dir = math.pi
        elif y <= 0:
            dir = -math.pi/2
        elif y >= game.H:
            dir = math.pi/2

        spawn_particles(x, y, 30, -dir)
        game.sfx.spawn_windup.play()

        self.delay_spawning_enemy(x, y, EnemyType, random.uniform(self.spawnRate/8, self.spawnRate*0.2))
    
    def draw(self, window):
        #drawText(window, f"Wave Timer: {round(self.timer)}s", (0,0,0), (game.W-200, 200), 40, True)
        drawText(window, f"Wave #{round(self.num)}", (255,255,255), (self.rect.center.x, self.rect.center.y+self.rect.w*0.75), 40, True, True)
        self.timer_img.draw(self.rect.copy(), window)
        n = math.floor(self.timer/8)
        if self.timer >= 59:
            n = 8
        self.timer_img.setState(f"{n}/8")
