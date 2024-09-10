import numpy as np
from library import *
import copy
import traceback

DEFAULT_GRAVITY = 1000
DEFUALT_AIRFRIC = 0.98
FIXED_TIMESTEP = 1/60

class Collider:
    def __init__(self, rect, tag):
        self.rect = rect
        self.tag = tag

    def check_collision(self, otherCollider):
        output = AABBCollision(self.rect, otherCollider.rect)
        return output

class Entity:
    def __init__(self, ID, rect, collisionTag, gameRef):
        self.rect = np.array(rect)
        self.collider = Collider(self.rect, collisionTag)
        self.id = ID
        self.game = gameRef

    def check_collision(self, otherEntity):
        if self.collider.check_collision(otherEntity.collider):
            self.on_collision(otherEntity)
            otherEntity.on_collision(self)

    def update(self, dt):
        print(f"update was not overriden! id: {self.id}")

    def draw(self, window):
        print(f"draw was not overriden! id: {self.id}")

    def on_collision(self, otherEntity):
        print(f"onCollision was not overriden! id: {self.id}")

    def get_center(self):
        return np.array([self.rect[0] + self.rect[2]/2, self.rect[1] + self.rect[3]/2])

class RigidBody(Entity):
    def __init__(
            self, 
            ID, rect, collisionTag, gameRef,
            grav=DEFAULT_GRAVITY,
            airFric=DEFUALT_AIRFRIC,
            inverseMass=1, # 1 / mass of obj
            coeffRestitution=0.1 # elasticity, 1 is perfectly bouncy
            ):

        super().__init__(ID, rect, collisionTag, gameRef)
        
        self.vel = np.array([0,0])
        self.forces = np.array([0,0])

        # physics properties
        self.gravity = grav
        self.airFric = airFric
        self.invMass = inverseMass
        self.coeffRestitution = coeffRestitution

    def update(self, dt):
        accel = np.multiply(self.forces, self.invMass)
        self.forces = np.array([0, self.gravity/self.invMass])

        self.vel = np.add(self.vel, np.multiply(accel, dt))
        self.vel = np.multiply(self.airFric, self.vel)

        self.rect = np.add(self.rect, np.array([self.vel[0], self.vel[1], 0, 0]))

        self.collider.rect = self.rect

    def handle_collision_with_static_body(self, otherEntity, mtv):
        offset = 1

        self.rect = np.add(self.rect, [mtv[0]*offset, mtv[1]*offset, 0,0])
        self.collider.rect = self.rect

        invM1 = self.invMass
        invM2 = 0
        norm = normalize(mtv)
        norm = np.array(norm)
        rel_vel = np.dot(self.vel, norm)
        et = self.coeffRestitution
        Vj = -(1 + et) * rel_vel
        J = Vj / (invM1 + invM2)

        self.apply_impulse(np.multiply(norm, np.array(J)))

    def handle_collision_with_rigid_body(self, otherEntity, mtv):
        offset = 0.5

        self.rect = np.add(self.rect, [mtv[0]*offset, mtv[1]*offset, 0,0])
        self.collider.rect = self.rect

        e_1 = self.coeffRestitution
        e_2 = otherEntity.coeffRestitution
        invM1 = self.invMass
        invM2 = otherEntity.invMass
        norm = np.array(normalize(mtv))
        rel_vel = np.dot(np.subtract(self.vel, otherEntity.vel), norm)
        et = max(e_1, e_2)
        Vj = -(1 + et) * rel_vel
        J = Vj / (invM1 + invM2)

        self.apply_impulse(np.multiply(norm, np.array(J)))

    def apply_impulse(self, J):
        self.vel = np.add(self.vel, np.multiply(self.invMass, J))

    def on_collision(self, otherEntity):
        mtv = self.collider.check_collision(otherEntity)

        if isinstance(otherEntity, RigidBody): # do rigidbody collision resolution
            self.handle_collision_with_rigid_body(otherEntity, mtv)
        elif isinstance(otherEntity, StaticBody): # do staticbody colliison resolution
            self.handle_collision_with_static_body(otherEntity, mtv)


class StaticBody(Entity):
    def __init__(self, ID, rect, collisionTag, gameRef):
        super().__init__(ID, rect, collisionTag, gameRef)

    def update(self, dt):
        pass # StaticBody doesnt update

    def on_collision(self, otherEntity):
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
    def __init__(self, gameRef, collisionRules, initEntities=[]):
        self.entities = {}
        # entities are stored as follows:
        # {"CollisionTag": {"id1": Entity, "id2": Entity}}
        # where both entities with id's "id1" and "id2" belong
        # to the "CollisionTag" Collision layer
        self.toRemove = []

        self.collisionRules = {}
        self.update_collision_rules(collisionRules)

        self.accumulator = 0 # this is for fixed timestep shenanigans

        self.game = gameRef

        for entity in initEntities:
            self.add_entity(copy.copy(entity))

    def update(self, dt):
        try:
            self.accumulator += dt
            while self.accumulator >= FIXED_TIMESTEP:
                # update each entity
                for tag in self.entities:
                    for ID in self.entities[tag]:
                        self.entities[tag][ID].update(FIXED_TIMESTEP)

                for entity in self.toRemove:
                    self.cleanup_entity(entity)
                self.toRemove = []

                self.resolve_collisions()

                self.accumulator -= FIXED_TIMESTEP
        except Exception as e:
            print("failed at world.update")
            traceback.print_exc()

    def draw(self, window):
        try:
            # draw each entity
            for tag in self.entities: # go thru each collision layer
                for ID in self.entities[tag]: # go thru each entity in said collis layer
                    self.entities[tag][ID].draw(window)
        except Exception as e:
            print("failed at world.draw")
            traceback.print_exc()

    def update_collision_rules(self, newCollisionRules): # kinda redundant
        self.collisionRules = newCollisionRules

    def cleanup_entity(self, entity):
        del self.entities[entity.collider.tag][entity.id]

    def add_entity(self, entity):
        try:
            self.entities[entity.collider.tag][entity.id] = entity
        except Exception as e:
            print(f"adding {e} to entity tags")
            self.entities[entity.collider.tag] = {}
            self.entities[entity.collider.tag][entity.id] = entity

    def delete_entity(self, entity):
        self.toRemove.append(entity)

    def check_collisions_of_entity(self, entity):
        for tag in self.collisionRules[entity.collider.tag]:
            try:
                # loop thru each tag in collision rules for corresponding entity
                for ID in self.entities[tag]:
                    # loop thru each entity per collision layer
                    if ID != entity.id:
                        otherEntity = self.entities[tag][ID]
                        entity.check_collision(otherEntity)
            except KeyError as e: # if does not exist make an empty dict
                self.entitiesToAdd.append(tag)
                print(f"{tag} did not exist in world.entities so empty dict was made")

    def resolve_collisions(self):
        self.entitiesToAdd = []
        for tag in self.entities: # go thru each collision layer
            for ID in self.entities[tag]: # go thru each entity in said collis layer
                self.check_collisions_of_entity(self.entities[tag][ID])

        for tag in self.entitiesToAdd:
            self.entities[tag] = {}


