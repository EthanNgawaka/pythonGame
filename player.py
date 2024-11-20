from game import *
from deck import *
from particles import *
from bullets import *
from status_effects import *

class PlayerUI(Entity):
    def __init__(self, player):
        self.player = player
        self.rect = Rect((100,100),(player.maxHealth*3,30))
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
        self.rect = Rect((x, y), (w, h))
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
        self.iFrames = 0.75

        # (implemented) #
        self.panic = 0
        self.piercing = 0
        self.speed = 50
        self.maxHealth = 150

        self.hotShot = 0

        self.kb = 500
        self.dmgMultiplier = 1
        self.dmg = 5
        self.baseDmg = 5
        self.atkRateMultiplier = 1
        self.atkRate= 0.35
        self.baseAtkRate = self.atkRate

        self.bulletCount = 1
        self.speedInaccuracy = 0 # +/- % ie 0.1 means +/- 10% speed
        self.inaccuracy = 0.13
        self.bulletSpeed = 20
        # ---------- #

        # random stuff #
        self.copper = 0 # coins
        self.health = self.maxHealth

        self.flashFreq = 0.2
        self.last_known_aim_dir = 0

        self.fire_theta = 0
        # ---------- #

        # timers #
        self.bulletCooldown = 0
        self.invincibilityTimer = 0
        self.hit_timer = 0
        # ------ #

        self.base_stats = self.get_stats()

        # Deck (Chips/Inventory)
        # the deck is an object that holds all the cards
        # when a shop is opened the cards are shown and when bought
        # a func called on_pickup is called
        # (this is ur basic stat changes, ie on_pickup(): player.speed += 10)
        # there is a passive func too which is updated every frame
        # TODO actives arent implemented yet but im going there next
        self.deck = Deck(self)

        # sprite stuff
        self.player_img = Image("./assets/player.png", *self.rect)
        self.gun_img = Image("./assets/gun.png", *self.rect)

    def get_list_of_status_effects_of_type(self, status_type):
        all_statuses = game.get_entities_by_type(status_type)
        filtered = [s for s in all_statuses if s.ent == self]
        return filtered
    def get_stacks_of_status_effects(self, status_type):
        return len(self.get_list_of_status_effects_of_type(status_type))
    
    def add_status_effect(self, status_type, stacks=1):
        # a status effect "stack" is just an entity that
        # changes something about another entity every frame
        # status effects can scale linearly, exponentially or whatever with stacks
        # although linear is the easiest (1 stack -5hp/s, 2stack -10hp/s etc)
        # exponential is possible to (example of this is fire)
        for _ in range(stacks):
            game.curr_scene.add_entity(status_type(self), "status player")

    def heal(self, amnt):
        self.health += amnt
        if self.health > self.maxHealth:
            self.health = self.maxHealth

    def reset_stats(self):
        self.set_stats(self.base_stats)
        self.deck = Deck(self)

    def set_stats(self, dict):
        for [name, val] in dict.items():
            setattr(self, name, val)

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
            "lifesteal", "piercing", "dmgMultiplier"
        ]
        out_dict = {}
        for stat_name in stat_names:
            out_dict[stat_name] = getattr(self, stat_name)

        return out_dict

    def bound_to_screen(self): # this is temp
        if self.rect.x < 0 and self.vel.x < 0:
            self.rect.x = 0
            self.vel.x = 0
        if self.rect.x+self.rect.w > game.W and self.vel.x > 0:
            self.rect.x = game.W - self.rect.w
            self.vel.x = 0

        if self.rect.y < 0 and self.vel.y < 0:
            self.rect.y = 0
            self.vel.y = 0
        if self.rect.y+self.rect.h > game.H and self.vel.y > 0:
            self.rect.y = game.H - self.rect.h
            self.vel.y = 0

    def physics(self, dt):
        self.move(self.vel*dt)
        self.vel *= self.drag

    def hit(self, ent):
        if self.invincibilityTimer <= 0:
            # this is for hitstop idk it feels kinda bad on every single hit
            #game.time_speed = 0.001
            #self.hit_timer = 0.05
            if ent.inflictFire:
                self.add_status_effect(Fire)
            self.health -= ent.dmg
            self.invincibilityTimer = self.iFrames

            self.speed *= 1 + 0.02*self.panic

            if isinstance(ent, EnemyBullet):
                vec = ent.vel.normalize()
                self.vel += vec * self.kb * 2
                return

            theta = vec_angle_to(
                pygame.Vector2(self.rect.center),
                pygame.Vector2(ent.rect.center)
            )
            vec = pygame.Vector2(math.cos(theta), math.sin(theta))
            self.vel -= vec * self.kb * 2

    def input(self):
        self.movement()
        self.shooting()

    def spawn_bullet(self, pos, theta):
        speed = self.bulletSpeed*(1+random.uniform(-self.speedInaccuracy, self.speedInaccuracy))
        vel = pygame.Vector2(math.cos(theta), math.sin(theta)) * (speed) * 60
        id = "bullet"

        game.curr_scene.add_entity(Bullet(pos, vel), id)

    # make controller shoot on right trigger
    def shooting(self):
        # mouse input 
        firing = game.mouse.down[0]
        theta = vec_angle_to(self.rect.center, game.mouse.pos)
        self.fire_theta = theta

        # controller input
        if game.input_mode == "controller":
            firing = game.controller.RTRIGGER
            if game.controller.RSTICK.length() > 0.5:
                theta = math.atan2(game.controller.RSTICK.y, game.controller.RSTICK.x)
                self.last_known_aim_dir = theta
            else:
                theta = self.last_known_aim_dir

        if self.curr_weapon == "gun":
            self.fire_theta = theta
            # focus on this for now once really solid base game add more weapons
            if self.bulletCooldown <= 0:
                if firing:
                    for i in range(self.bulletCount):
                        rand_angle = random.uniform(-self.inaccuracy, self.inaccuracy)
                        spawn_pos = (self.rect.center.x + math.sin(-theta + 1.6) * 55, self.rect.center.y + math.cos(-theta + 1.6) * 55)
                        self.spawn_bullet(spawn_pos, theta + rand_angle)
                        self.vel -= pygame.Vector2(math.cos(theta), math.sin(theta))*60

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

    def game_over(self):
        game.switch_to_scene("menu")
        self.remove_self()

    # always keep update and draw at bottom
    def update(self, dt):
        self.input()
        self.physics(dt)
        self.bound_to_screen()

        if game.key_pressed(pygame.K_SPACE):
            self.add_status_effect(Acid)

        # increment / decrement all timers
        self.bulletCooldown -= dt
        self.invincibilityTimer -= dt

        if self.health <= 0:
            self.game_over()

    def draw(self, window):
        # flashing logic
        if self.invincibilityTimer > 0 and math.ceil(self.invincibilityTimer/self.flashFreq) % 2 == 0:
            return

        self.player_img.draw_rotated(window, self.rect.scale(2,2))
        dir = -1
        if self.vel.x < 0:
            dir = 1
        self.player_img.rot += dir*math.pi*self.vel.length()/100


        #---------------# GUN DRAWING #---------------#
        # idk why theta needs to be multiplied by -1 but unless i do it goes weird
        theta = self.fire_theta * -1
        self.gun_img.rect = self.rect.scale(2,2)

        # this part makes it so the gun isnt overlapping with the player and is drawn a a bit away from the center
        # py module math. uses radians and 1.5 makes the gun line up with the mouse
        self.gun_img.rect.x += math.sin(theta + 1.5) * 50
        self.gun_img.rect.y += math.cos(theta + 1.5) * 50

        # .draw_rotated uses degrees so multiply theta by 57.2958 to get the degrees instead of radians
        self.gun_img.rot = theta * 57.2958
        self.gun_img.draw_rotated(window, self.gun_img.rect)
        #-------------------------------------------#