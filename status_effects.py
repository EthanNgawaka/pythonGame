from game import *
from particles import *

class Acid(Entity):
    def __init__(self, entity):
        self.ent = entity
        self.fire_spawn_rate = random.uniform(0.01,0.05)
        self.timer = 5
        self.last_fire_spawn = self.timer
        # this gobbledy gook just makes it so
        # all the stacks timers are reset when a new one is added and
        # each stack fades gradually and not all at once
        all_other_effects = self.ent.get_list_of_status_effects_of_type(self.__class__)
        for i in range(len(all_other_effects)):
            all_other_effects[i].timer = self.timer*(i+2)

    def update(self, dt):
        if self.timer > 0 and self.ent in game.curr_scene.entities.values():
            ls = self.ent.get_list_of_status_effects_of_type(self.__class__)
            self.timer -= dt
            self.ent.atkRate = self.ent.baseAtkRate*2

            # particles
            if abs(self.timer-self.last_fire_spawn) > self.fire_spawn_rate and ls[0] == self:
                self.last_fire_spawn = self.timer
                spawn_acid_particle(*self.ent.rect.center)
        else:
            self.ent.atkRate = self.ent.baseAtkRate
            self.remove_self()

    def draw(self, window):
        ls = self.ent.get_list_of_status_effects_of_type(self.__class__)
        if ls[0] == self:
            drawText(
                window, f"ACID: {len(ls)}", (0,128,0),
                self.ent.rect.center+pygame.Vector2(0,self.ent.rect.h),
                45, True
            )

class Weakness(Entity):
    def __init__(self, entity):
        self.ent = entity
        self.fire_spawn_rate = random.uniform(0.01,0.05)
        self.timer = 5
        self.last_fire_spawn = self.timer
        # this gobbledy gook just makes it so
        # all the stacks timers are reset when a new one is added and
        # each stack fades gradually and not all at once
        all_other_effects = self.ent.get_list_of_status_effects_of_type(self.__class__)
        for i in range(len(all_other_effects)):
            all_other_effects[i].timer = self.timer*(i+2)

    def update(self, dt):
        if self.timer > 0 and self.ent in game.curr_scene.entities.values():
            ls = self.ent.get_list_of_status_effects_of_type(self.__class__)
            self.timer -= dt
            self.ent.dmg = self.ent.baseDmg/2

            # particles
            if abs(self.timer-self.last_fire_spawn) > self.fire_spawn_rate and ls[0] == self:
                self.last_fire_spawn = self.timer
                spawn_weakness_particle(*self.ent.rect.center)
        else:
            self.ent.dmg = self.ent.baseDmg
            self.remove_self()

    def draw(self, window):
        ls = self.ent.get_list_of_status_effects_of_type(self.__class__)
        if ls[0] == self:
            drawText(
                window, f"WEAKNESS: {len(ls)}", (255,0,0),
                self.ent.rect.center+pygame.Vector2(0,self.ent.rect.h),
                45, True
            )

class Fire(Entity):
    def __init__(self, entity):
        self.ent = entity
        self.fire_spawn_rate = random.uniform(0.05,0.2)
        self.timer = 3
        self.last_fire_spawn = self.timer
        # this gobbledy gook just makes it so
        # all the stacks timers are reset when a new one is added and
        # each stack fades gradually and not all at once
        all_other_effects = self.ent.get_list_of_status_effects_of_type(self.__class__)
        for i in range(len(all_other_effects)):
            all_other_effects[i].timer = self.timer*(i+2)

    def update(self, dt):
        if self.ent.fire_immunity:
            self.remove_self()
            return

        if self.timer > 0 and self.ent in game.curr_scene.entities.values():
            self.timer -= dt
            stacks = self.ent.get_stacks_of_status_effects(self.__class__)
            self.ent.take_dmg(dt*math.pow(1.3, stacks)/stacks)
            # div by stacks here means that by the time all the stacks
            # apply their individual health deductions
            # we end up with the entity losing
            # 1.5^(stacks) hp/sec
            # these numbers are wrong cause balance tweaks but still
            # fine illustration
            # eg: 2 stacks = 2.25hp/s, 4 stacks = 5hp/s,
            #     6 stacks = 12hp/s, 8 stacks = 26hp/s
            if abs(self.timer-self.last_fire_spawn) > self.fire_spawn_rate:
                self.last_fire_spawn = self.timer
                spawn_fire(*self.ent.rect.center)
        else:
            self.remove_self()

    def draw(self, window):
        ls = self.ent.get_list_of_status_effects_of_type(self.__class__)
        if ls[0] == self:
            drawText(
                window, f"FIRE: {len(ls)}", (255,0,0),
                self.ent.rect.center+pygame.Vector2(0,self.ent.rect.h),
                45, True
            )

