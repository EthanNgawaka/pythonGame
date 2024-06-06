from library import *

class BasicEnemy:
    def __init__(self, x, y):
        self.rect = [x,y,30,30]
        self.r = self.rect[2]/2
        self.col = (255,0,0)
        self.vel = [0,0]
        self.speed = 800
        self.health = 20
        self.forces = [0,0]
        self.invMass = 1
        self.contactDmg = 5
        self.contactKnockback = 200

    def draw(self, window):
        if self.health > 0:
            drawCircle(window,((self.rect[0]+self.r,self.rect[1]+self.r),self.r),self.col)

    def update(self, window, player, dt, enemiesOnScreen):
        if self.health > 0:
            self.trackPlayer(player.rect)
            self.physics(dt)
            self.collisions(player, enemiesOnScreen)

    def collisions(self, player, enemiesOnScreen):
        collisionCheck = AABBCollision(self.rect, player.rect)
        if collisionCheck:
            knockbackVec = scalMult(collisionCheck, self.contactKnockback/magnitude(collisionCheck))
            player.takeDmg(self.contactDmg, scalMult(knockbackVec, -1), self)

        for bullet in player.bullets:
            check = AABBCollision(self.rect,bullet.rect)
            if check:
                self.health -= player.dmg
                player.bullets.remove(bullet)
                if self.health <= 0:
                    enemiesOnScreen.remove(self)
                    break

    def physics(self, dt):
        fric = 0.98
        accel = [self.forces[0]*self.invMass,self.forces[1]*self.invMass]
        self.vel[0] += accel[0]*dt
        self.vel[1] += accel[1]*dt
        self.rect[0] += self.vel[0]*dt
        self.rect[1] += self.vel[1]*dt
        self.vel = [self.vel[0]*fric,self.vel[1]*fric]
        self.forces = [0,0]

    def trackPlayer(self, playerRect):
        dir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
        magnitude = math.sqrt(dir[0]**2 + dir[1]**2)
        if magnitude != 0:
            moveSpeed = self.speed/magnitude
            self.forces[0] += moveSpeed * dir[0]
            self.forces[1] += moveSpeed * dir[1]

	