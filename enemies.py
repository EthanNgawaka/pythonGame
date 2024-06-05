from library import *

class BasicEnemy:
	def __init__(self, x, y):
		self.rect = [x,y,20,20]
		self.r = self.rect[2]/2
		self.col = (255,0,0)
		self.vel = [0,0]
		self.speed = 0.01
		self.health = 20
		self.forces = [0,0]
		self.invMass = 0.01

	def draw(self, window):
		drawCircle(window,((self.rect[0]+self.r,self.rect[1]+self.r),self.r),self.col)

	def update(self, window, playerRect, dt):
		self.trackPlayer(playerRect)
		self.physics(dt)

	def physics(self, dt):
		accel = [self.forces[0]*self.invMass,self.forces[1]*self.invMass]
		self.vel[0] += accel[0]*dt
		self.vel[1] += accel[1]*dt
		self.rect[0] += self.vel[0]*dt
		self.rect[1] += self.vel[1]*dt
		self.vel = [self.vel[0]*0.9,self.vel[1]*0.9]

	def trackPlayer(self, playerRect):
		dir = [playerRect[0] - self.rect[0], playerRect[1] - self.rect[1]]
		magnitude = math.sqrt(dir[0]**2 + dir[1]**2)
		if magnitude != 0:
			moveSpeed = self.speed/magnitude
			self.forces[0] += moveSpeed * dir[0]
			self.forces[1] += moveSpeed * dir[1]

	