import numpy as np

DEFAULT_GRAVITY = 2000
DEFUALT_AIRFRIC = 0.98
FIXED_TIMESTEP = 1/60

class Collider:
    def __init__(self, rect, tag):
        self.rect = rect
        self.tag = tag

    def check_collision(otherCollider, colliderType="rect"):
        return AABBCollision(self.rect, otherCollider.rect)

class Entity:
    def __init__(self, ID, rect, collisionTag):
        self.rect = np.array(rect)
        self.collider = Collider(self.rect, self.collisionTag)
        self.id = ID

    def check_collision(otherEntity):
        if self.collider.check_collision(otherEntity.collider):
            self.on_collision(otherEntity)
            otherEntity.on_collision(self)

    def update(dt):
        print(f"update was not overriden! id: {self.id}")

    def draw():
        print(f"draw was not overriden! id: {self.id}")

    def on_collision(otherEntity):
        print(f"onCollision was not overriden! id: {self.id}")

    def get_center():
        return np.array([self.rect[0] + self.rect[2]/2, self.rect[1] + self.rect[3]/2])

class RigidBody(Entity):
    def __init__(ID, rect, collisionTag, inverseMass):
        super(ID, rect, collisionTag)

        self.invMass = inverseMass
        
        self.vel = np.array([0,0])
        self.forces = np.array([0,0])
        self.gravity = DEFAULT_GRAVITY
        self.airFric = DEFUALT_AIRFRIC

    def update(dt):
        accel = np.multiply(self.forces, self.invMass)
        self.forces = np.array([0, self.gravity/self.invMass])

        self.vel = np.add(self.vel, np.multiply(accel, dt))
        self.vel = np.multiply(self.airFric, self.vel)

        self.rect = np.add(self.rect, np.array([self.vel[0], self.vel[1], 0, 0]))

        self.collider.rect = self.rect

    def handle_collision_with_static_body(otherEntity, mtv):
        pass

    def handle_collision_with_rigid_body(otherEntity, mtv):
        # we dont realllllly need this cause 
        # A) my physics resolution is ass
        # B) no real rigid body on rigid body collisions in the game (maybe particles?)
        pass 

    def on_collision(otherEntity):
        super.on_collision(otherEntity)

class StaticBody(Entity):
    def __init__(ID, rect, collisionTag):
        super(ID, rect, collisionTag)

    def update(dt):
        pass # StaticBody doesnt update

    def onCollision(otherEntity):
        pass # Just so it doesnt NEED to be overriden by children

# a World contains a list of entities which have basic functions like
# - draw
# - update
# - on_collision
# - etc

# A World is responsible for updating and drawing all entities
# A World has an obj, "Collision Rules"
# Eg) "Player" : ["Wall", "Enemy"]
# This reads as: "any entity with the collision tag "Player", should collide with
# any entities with the tags "Wall" or "Enemy" "

class World:
    def __init__(self, collisionRules, initEntities=[]):
        self.entities = {}
        # entities are stored as follows:
        # {"CollisionTag": {"id1": Entity, "id2": Entity}}
        # where both entities with id's "id1" and "id2" belong
        # to the "CollisionTag" Collision layer
        self.toRemove = []

        self.collisionRules = {}
        self.updateCollisionRules(collisionRules)

        self.accumulator = 0 # this is for fixed timestep shenanigans

        for entity in initEntities:
            self.add_entity(entity)

    def update(self, dt):
        self.accumulator += dt
        while self.accumulator >= FIXED_TIMESTEP:
            # update each entity
            for tag in self.entities:
                for ID in self.entities[tag]:
                    self.entites[tag][ID].update(FIXED_TIMESTEP)

            for let ID, tag of self.toRemove:
                self.cleanup_entity(entity.id, entity.collider.tag)
            self.toRemove = []

            self.resolve_collisions()

            self.accumulator -= FIXED_TIMESTEP

    def draw(self):
        # draw each entity
        for tag in self.entities: # go thru each collision layer
            for ID in self.entities[tag]: # go thru each entity in said collis layer
                self.entites[tag][ID].draw()

    def update_collision_rules(self, newCollisionRules): # kinda redundant
        self.collisionRules = newCollisionRules

    def cleanup_entity(self, entity):
        del self.entities[tag][ID]

    def add_entity(self, entity):
        self.entities[entity.collider.tag][entity.id] = entity

    def delete_entity(self, entity):
        self.toRemove.append(entity)

    def check_collisions_of_entity(self, entity):
        for tag in self.collisionRules[entity.collider.tag]:
            # loop thru each tag in collision rules for corresponding entity
            for ID in self.entites[tag]:
                # loop thru each entity per collision layer
                if ID != entity.id:
                    otherEntity = self.entities[tag][ID]
                    entity.check_collision(otherEntity)

    def resolve_collisions(self):
        for tag in self.entities: # go thru each collision layer
            for ID in self.entities[tag]: # go thru each entity in said collis layer
                self.check_collisions_of_entity(self.entites[tag][ID])

