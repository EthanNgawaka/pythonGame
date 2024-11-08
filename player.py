from game import *
from deck import *

class PlayerUI(Entity):
    def __init__(self, player):
        self.player = player
        self.rect = pygame.Rect(100,100,player.maxHealth*3,30)
        self.isUI = True
        self.greenBarW = self.rect.w
        self.orangeBarW = self.rect.w
        self.oldHpTimer = 0
        self.orangeBarDelay = 1

    def draw_hp_bar(self, window):
        diffFromMaxHealth = self.player.maxHealth - self.player.health

        greenRect = self.rect.copy()
        greenRect.w = self.greenBarW
        self.greenBarW = lerp(self.greenBarW, self.player.health*3, 0.02)

        orangeRect = self.rect.copy()
        orangeRect.w = self.orangeBarW
        if self.oldHpTimer <= 0:
            self.orangeBarW = lerp(self.orangeBarW , self.player.health*3, 0.1)

        drawRect(window, self.rect, (255,0,0))
        drawRect(window, orangeRect, (255,140,0))
        drawRect(window, greenRect, (0,255,0))


    def draw_copper(self, window):
        drawText(window, f"Copper: {self.player.copper}", (255, 153, 51), (100,150), 40)

    def draw_stats(self, window):
        i = 0
        for stat_name, stat_val in self.player.get_stats().items():
            drawText(window, f"{stat_name}: {stat_val}", (0,0,0), (50,250+40*i), 20)
            i+=1

    def draw(self, window):
        self.draw_hp_bar(window)
        self.draw_copper(window)
        if DEBUG:
            self.draw_stats(window)

    def update(self, dt):
        self.oldHpTimer -= dt
        if self.player.invincibilityTimer > 0:
            self.oldHpTimer = self.orangeBarDelay

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
        # (NOT implemented) #
        self.lifesteal = 0
        self.piercing = 0
        self.iFrames = 1.5

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

        # random stuff #
        self.copper = 0 # coins
        self.health = self.maxHealth

        self.flashFreq = 0.2
        # ---------- #

        # timers #
        self.bulletCooldown = 0
        self.invincibilityTimer = 0
        # ------ #

        # Deck (Chips/Inventory)
        # the deck is an object that holds all the cards
        # when a shop is opened the cards are shown and when bought
        # a func called on_pickup is called
        # (this is ur basic stat changes, ie on_pickup(): player.speed += 10)
        # there is a passive func too which is updated every frame
        # TODO actives arent implemented yet but im going there next
        self.deck = Deck(self)

    def get_stats(self):
        # TODO: would be cool to have a slider for each stat in debug
        # for testing purposes

        # this is awesome i didnt know this but you can
        # use getattr(object, "name_of_attr")
        # to get the attribute of an object from a string
        # ie you know the player obj has an attr "health"
        # you can do getattr(player, "health) and it returns player.health
        # super neat for this so all you need to do for new player
        # attributes is add it to the stat_names list below 
        # (same for setattr)
        stat_names = [
            "atkRate", "speed", "dmg", "maxHealth",
            "atkRateMultiplier", "kb", "bulletCount",
            "speedInaccuracy", "inaccuracy", "bulletSpeed",
            "lifesteal", "piercing"
        ]
        out_dict = {}
        for stat_name in stat_names:
            out_dict[stat_name] = getattr(self, stat_name)

        return out_dict

    def bound_to_screen(self): # this is temp
        if self.rect.x < 0 and self.vel.x < 0:
            self.rect.x = 0
            self.vel.x = 0
        if self.rect.x+self.rect.w > W and self.vel.x > 0:
            self.rect.x = W - self.rect.w
            self.vel.x = 0

        if self.rect.y < 0 and self.vel.y < 0:
            self.rect.y = 0
            self.vel.y = 0
        if self.rect.y+self.rect.h > H and self.vel.y > 0:
            self.rect.y = H - self.rect.h
            self.vel.y = 0

    def physics(self, dt):
        self.move(self.vel*dt)
        self.vel *= self.drag

    def hit(self, ent):
        if self.invincibilityTimer <= 0:
            self.health -= ent.dmg
            self.invincibilityTimer = self.iFrames

    def input(self):
        self.movement()
        self.shooting()

    def spawn_bullet(self, pos, theta):
        speed = self.bulletSpeed*(1+random.uniform(-self.speedInaccuracy, self.speedInaccuracy))
        vel = pygame.Vector2(math.cos(theta), math.sin(theta)) * (speed)
        id = "bullet"

        game.curr_scene.add_entity(Bullet(pos, vel), id)

    def shooting(self):
        # mouse input 
        firing = game.mouse.down[0]
        theta = vec_angle_to(self.rect.center, game.mouse.pos)

        # controller input
        if game.input_mode == "controller":
            firing = game.controller.RSTICK.length() > 0
            theta = math.atan2(game.controller.RSTICK.y, game.controller.RSTICK.x)

        if self.curr_weapon == "gun":
            # focus on this for now once really solid base game add more weapons
            if self.bulletCooldown <= 0:
                if firing:
                    for i in range(self.bulletCount):
                        rand_angle = random.uniform(-self.inaccuracy, self.inaccuracy)
                        self.spawn_bullet(self.rect.center, theta + rand_angle)

                    self.bulletCooldown = self.atkRate / self.atkRateMultiplier

    def get_movement_dir_from_controller(self):
        movementDir = pygame.Vector2()
        # get move dir from controller
        movementDir.x = game.controller.LSTICK[0]
        movementDir.y = game.controller.LSTICK[1]
        # normalize if length > 0
        if movementDir.length() > 1:
            movementDir = movementDir.normalize()
        return movementDir

    def get_movement_dir_from_keyboard(self):
        movementDir = pygame.Vector2()
        # get move dir from keyboard
        if game.key_down(self.controls["up"]):
            movementDir.y -= 1
        if game.key_down(self.controls["down"]):
            movementDir.y += 1
        if game.key_down(self.controls["left"]):
            movementDir.x -= 1
        if game.key_down(self.controls["right"]):
            movementDir.x += 1
        if movementDir.length() != 0:
            movementDir = movementDir.normalize()
        return movementDir

    def movement(self):
        movementDir = self.get_movement_dir_from_keyboard() if game.input_mode == "keyboard" else self.get_movement_dir_from_controller()
        
        if movementDir.length() != 0:
            # stuff like this works because of pygame.Vector2()
            # super cool i dont have to implement this myself
            self.vel += movementDir * self.speed

    # always keep update and draw at bottom
    def update(self, dt):
        self.input()
        self.physics(dt)
        self.bound_to_screen()

        # increment / decrement all timers
        self.bulletCooldown -= dt
        self.invincibilityTimer -= dt

    def draw(self, window):
        # flashing logic
        if self.invincibilityTimer > 0 and math.ceil(self.invincibilityTimer/self.flashFreq) % 2 == 0:
            return

        drawCircle(window, (self.rect.center, self.rect.w/2), self.col)

# ======================================================================= #
class Bullet(Entity):
    def __init__(self, center, vel):
        player = game.get_entity_by_id("player")

        self.r = self.get_size(player.dmg*player.dmgMultiplier)
        self.rect = pygame.Rect((0,0), (self.r*2, self.r*2))
        self.rect.center = center

        self.vel = vel

        self.piercesLeft = player.piercing
        self.piercedEnemies = []

    def has_not_pierced(self, enemy):
        for e in self.piercedEnemies:
            if e == enemy:
                return False
        return True

    def get_size(self,x):
        return max(x*1.6, 4)
    
    def on_enemy_collision(self, enemy):
        self.piercesLeft -= 1
        self.piercedEnemies.append(enemy)

        if self.piercesLeft < 0:
            self.remove_self()

    def update(self, dt):
        self.move(self.vel)
        if not AABBCollision(self.rect, [0,0,W,H]):
            self.remove_self()

    def draw(self, window):
        drawCircle(window, (self.rect.center, self.r), (255,255,0))
