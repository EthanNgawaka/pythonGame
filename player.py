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

        self.flash_timer = 0
        self.flash_limit = 0.2
        self.last_flash = 0
        self.static_index = 0
        self.static_colors = [pygame.Color("#2092be"), pygame.Color("#53d0ff")]

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

    def draw_static_discharge(self, window):
        if self.player.static_discharge > 0:
            static_discharge_rect = Rect((0,0),(self.player.rect.w*2.5, self.player.rect.h*0.3))
            static_discharge_rect.center = self.player.rect.center - pygame.Vector2(0,self.player.rect.h)
            drawRect(window, static_discharge_rect, pygame.Color("grey"))
            charge_rect = static_discharge_rect.copy()
            t = min(1,self.player.static_discharge_timer/self.player.static_discharge_max)
            drawRect(window, charge_rect.scale(t,1), self.static_colors[self.static_index])
            if t == 1:
                if abs(self.flash_timer - self.last_flash) >= self.flash_limit:
                    self.last_flash = self.flash_timer
                    self.static_index = 1 if self.static_index == 0 else 0
            else:
                self.static_index = 0

    def draw(self, window):
        self.draw_hp_bar(window)
        self.draw_copper(window)
        #if DEBUG:
        #    self.draw_stats(window)

        self.draw_static_discharge(window)

    def update(self, dt):
        self.flash_timer += dt
        self.oldHpTimer -= dt
        if self.player.invincibilityTimer > 0:
            self.oldHpTimer = self.orangeBarDelay

class AOEBlast(Entity):
    def __init__(self, r, center, dmg):
        self.max_r = r
        self.r = 0
        self.rect = Rect((0,0), (r*2, r*2))
        self.rect.center = center
        self.player = game.get_entity_by_id("player")
        self.dmg = dmg

        self.timer = 0
        self.lifetime = 0.7

        self.shrink = False
        game.time_speed = 0.2

        for e in game.get_entities_by_id("enemy"):
            if AABBCollision(self.rect, e.rect):
                if isinstance(e, EnemyBullet):
                    e.remove_self()
                    continue
                e.hit(self.dmg, (self.rect.center-e.rect.center).normalize()*25)

    def ease_out_elastic(self, t):
        if t == 0:
            return 0
        if t == 1:
            return 1
        c4 = 2*math.pi/3
        return math.pow(2,-10*t)*math.sin((t*10-0.75)*c4)+1

    def update(self, dt):
        t = self.timer/self.lifetime
        if t >= 0.54:
            self.shrink = True

        if self.shrink:
            self.timer -= dt*2
            self.r = lerp(self.r, 0, 0.5)
            if self.timer <= 0:
                self.remove_self()
        else:
            self.r = self.ease_out_elastic(t)*self.max_r
            self.timer += dt

    def draw(self, window):
        drawCircle(window,(self.rect.center,self.r),pygame.Color("#53d0ff"))

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

        # (implemented) #
        self.blood_bullets = 0
        self.coin_gun = 0
        self.bulletSize = 1
        self.iFrames = 0.75
        self.fire_immunity = False
        self.static_discharge = 0
        self.shield = 0
        self.curr_shield = 0
        self.lifesteal = 0
        self.panic = 0
        self.piercing = 0
        self.speed = 50
        self.maxHealth = 150

        self.hotShot = 0
        self.bouncy_bullets = False

        self.kb = 500
        self.dmgMultiplier = 1
        self.dmg = 5
        self.baseDmg = 5
        self.atkRateMultiplier = 1
        self.atkRate= 0.35
        self.baseAtkRate = self.atkRate
        self.dmg_taken_multiplier = 1

        self.bulletCount = 1
        self.speedInaccuracy = 0 # +/- % ie 0.1 means +/- 10% speed
        self.inaccuracy = 0.13
        self.bulletSpeed = 20
        self.phoenix = False
        # ---------- #

        # random stuff #
        self.copper = 0 # coins
        self.health = self.maxHealth

        self.flashFreq = 0.2
        self.last_known_aim_dir = 0

        self.fire_theta = 0
        self.gun_jiggle = 0
        # ---------- #

        # timers #
        self.bulletCooldown = 0
        self.invincibilityTimer = 0
        self.hit_timer = 0
        self.static_discharge_timer = 0 # so this increases faster with higher levels of it
        self.static_discharge_max = 8
        self.phoenix_timer = 0
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
            "lifesteal", "piercing", "dmgMultiplier",
            "hotShot", "bulletSize", "iFrames",
            "shield", "panic", "bouncy_bullets",
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
        self.vel *= self.drag if game.time_speed >= 1 else 1

    def AOE_blast(self, radius, dmg):
        game.curr_scene.add_entity(AOEBlast(radius,self.rect.center,dmg), "aoe player blast", "bottom")
        camera.shake(40,0.7)

    def take_dmg(self, amnt):
        self.health -= amnt * self.dmg_taken_multiplier

    def hit(self, ent):
        if self.invincibilityTimer <= 0:
            camera.shake(40)
            # this is for hitstop idk it feels kinda bad on every single hit
            #game.time_speed = 0.001
            #self.hit_timer = 0.05
            if self.curr_shield > 0:
                self.curr_shield -= 1
                self.invincibilityTimer = self.iFrames
                return
            if ent.inflictFire:
                self.add_status_effect(Fire)

            self.take_dmg(ent.dmg)
            self.invincibilityTimer = self.iFrames

            self.speed *= 1 + 0.02*self.panic

            if self.static_discharge_timer > 0:
                if self.static_discharge_timer >= self.static_discharge_max:
                    self.AOE_blast(250,10*self.static_discharge)
                self.static_discharge_timer = 0


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

    def new_wave(self):
        self.curr_shield = self.shield

    def get_pos_of_tip_of_gun(self):
        theta = self.fire_theta * -1 + self.gun_jiggle
        tip = self.gun_img.rect.center
        off = 3
        if abs(self.fire_theta) > math.pi/2:
            off = 0
        tip += pygame.Vector2(math.sin(theta+off), math.cos(theta+off))*10
        return tip

    def spawn_bullet(self, pos, theta):
        self.copper -= self.coin_gun*3 # 3 coins per level of coin gun
        self.take_dmg(self.blood_bullets)

        speed = self.bulletSpeed*(1+random.uniform(-self.speedInaccuracy, self.speedInaccuracy))
        vel = pygame.Vector2(math.cos(theta), math.sin(theta)) * (speed) * 60
        id = "bullet"

        if abs(self.fire_theta) > math.pi/2:
            # if aiming to the left
            self.gun_jiggle += random.uniform(-math.pi/8, 0)
        else:
            self.gun_jiggle += random.uniform(math.pi/8, 0)

        if self.atkRateMultiplier > 2:
            camera.shake(3)
        blt = Bullet(pos, vel)
        blt.bouncy = self.bouncy_bullets
        game.curr_scene.add_entity(blt, id)

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
                        # this logic didnt quite work
                        #spawn_pos = (self.rect.center.x + math.sin(-theta + 1.6) * 55, self.rect.center.y + math.cos(-theta + 1.6) * 55)
                        spawn_pos = self.get_pos_of_tip_of_gun()
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
        if self.phoenix:
            self.phoenix = False
            self.health = self.maxHealth
            self.atkRate /= 2
            self.dmg *= 2
            self.invincibilityTimer = 10
            self.phoenix_timer = 10
            # this makes it so no enemies drop coins because
            # this ability is already kinda broken
            for e in game.get_entities_by_id('enemy'):
                e.value = 0
            self.AOE_blast(game.W, 100)
            return

        game.switch_to_scene("menu")
        self.remove_self()

    # always keep update and draw at bottom
    def update(self, dt):
        self.input()
        self.physics(dt)
        self.bound_to_screen()

        # increment / decrement all timers
        self.bulletCooldown -= dt
        self.invincibilityTimer -= dt
        self.static_discharge_timer += dt * self.static_discharge # higher level faster recharge
        if self.phoenix_timer > 0:
            self.phoenix_timer -= dt
            spawn_fire(*self.rect.center)
            if self.phoenix_timer <= 0:
                self.dmg = self.baseDmg
                self.atkRate = self.baseAtkRate

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
        theta = self.fire_theta * -1 + self.gun_jiggle
        self.gun_img.rect = self.rect.scale(2,2)
        self.gun_jiggle = lerp(self.gun_jiggle, 0, 0.1)

        # this part makes it so the gun isnt overlapping with the player and is drawn a a bit away from the center
        # py module math. uses radians and 1.5 makes the gun line up with the mouse
        self.gun_img.rect.x += math.sin(theta + 1.5) * 50
        self.gun_img.rect.y += math.cos(theta + 1.5) * 50

        # .draw_rotated uses degrees so multiply theta by 57.2958 to get the degrees instead of radians
        self.gun_img.rot = theta * 57.2958 # gun jiggle hear just lerps to 0 and is set to a rand val when shooting to make it look jiggley
        if abs(self.fire_theta) > math.pi/2:
            self.gun_img.draw_rotated_and_flipped(window, self.gun_img.rect, False,True)
        else:
            self.gun_img.draw_rotated(window, self.gun_img.rect)

        #drawCircle(window, (self.get_pos_of_tip_of_gun(), 10), (255,0,0))
        #-------------------------------------------#
