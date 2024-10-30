from game import *

class Player(Entity):
    def __init__(self, x, y):
        w, h = 40, 40
        self.rect = pygame.Rect(x, y, w, h)
        self.vel = pygame.Vector2() # [0,0]
        self.curr_weapon = "gun"
        self.col = (127, 35, 219)
        self.controls = {
                "up": pygame.K_w,
                "left": pygame.K_a,
                "down": pygame.K_s,
                "right": pygame.K_d,
        }
        
        # physics consts #
        self.drag = 0.9
        # -------------- #

        # attributes #
        # (implemented) #
        self.speed = 50
        self.maxHealth = 100

        self.kb = 500
        self.dmgMultiplier = 1
        self.dmg = 5
        self.atkRateMultiplier = 1
        self.atkRate= 0.35

        self.bulletCount = 1
        self.speedInaccuracy = 0 # +/- % ie 0.1 means +/- 10% speed
        self.inaccuracy = 0.13
        self.bulletSpeed = 20
        # (NOT implemented) #
        # ---------- #

        self.copper = 0 # coins
        self.health = self.maxHealth

        # timers #
        self.bulletCooldown = 0

        # ------ #

        # Deck (Chips/Inventory) read deck.py for more info

    def move(self, vec):
        self.rect = self.rect.move(vec)

    def physics(self, dt):
        self.move(self.vel*dt)
        self.vel *= self.drag

    def input(self):
        self.movement()
        self.shooting()

    def spawn_bullet(self, pos, theta):
        speed = self.bulletSpeed*(1+random.uniform(-self.speedInaccuracy, self.speedInaccuracy))
        vel = pygame.Vector2(math.cos(theta), math.sin(theta)) * (speed)
        id = "bullet"
        game.curr_scene.add_entity(Bullet(pos, vel), id)

    def shooting(self):
        theta = vec_angle_to(self.rect.center, game.mouse.pos)

        if self.curr_weapon == "gun":
            # focus on this for now once really solid base game add more weapons
            if self.bulletCooldown <= 0:
                if game.mouse.down[0]:
                    for i in range(self.bulletCount):
                        rand_angle = random.uniform(-self.inaccuracy, self.inaccuracy)
                        self.spawn_bullet(self.rect.center, theta + rand_angle)

                    self.bulletCooldown = self.atkRate * self.atkRateMultiplier

    def movement(self):
        movementDir = pygame.Vector2()
        if game.key_down(self.controls["up"]):
            movementDir.y -= 1
        if game.key_down(self.controls["down"]):
            movementDir.y += 1
        if game.key_down(self.controls["left"]):
            movementDir.x -= 1
        if game.key_down(self.controls["right"]):
            movementDir.x += 1

        if movementDir.length() != 0:
            # stuff like this works because of pygame.Vector2()
            # super cool i dont have to implement this myself
            self.vel += movementDir.normalize() * self.speed

    # always keep update and draw at bottom
    def update(self, dt):
        self.input()
        self.physics(dt)

        # increment / decrement all timers
        self.bulletCooldown -= dt

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.rect.w/2), self.col)

# ======================================================================= #
class Bullet(Entity):
    def __init__(self, center, vel):
        player = game.get_entity_by_id("player")

        self.r = self.get_size(player.dmg*player.dmgMultiplier)
        self.rect = pygame.Rect((0,0), (self.r*2, self.r*2))
        self.rect.center = center
        self.vel = vel

    def get_size(self,x):
        # idk yet i just fucked around in desmos with tanh(x)
        # kinda assumes 30 is the highest dmg youll get
        return 10*math.tanh(0.1*(x-15))+17

    def move(self, vec):
        self.rect = self.rect.move(vec)

    def update(self, dt):
        self.move(self.vel)
        if not AABBCollision(self.rect, [0,0,W,H]):
            self.remove_self()

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.r), (255,255,0))
