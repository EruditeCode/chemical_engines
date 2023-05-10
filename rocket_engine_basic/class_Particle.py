import math
import numpy as np
from matrix_and_line_functions import get_unit_vector, get_vector_unit_normal, get_gradient_and_constant, intersect

class Particle:
	def __init__(self, pos, vel, rad):
		self.pos = np.array((pos[0], pos[1]))
		self.vel = np.array((vel[0], vel[1]))
		self.rad = rad
		self.movement_ratio = 1.0
		self.color = (240,240,40)

	def update_particle_collision(self, particles):
		for i in range(len(particles)-1, -1, -1):
			particle = particles[i]
			if particle == self:
				particles.pop(i)
			elif self.check_collision(particle):
				self.separate_atom_to_edge(particle)
				self.elastic_collision(self, particle)
		return particles

	def update_wall_collision(self, wall, dt):
		wall_length = math.dist(wall[0], wall[1])
		A2 = abs((wall[0][0]*wall[1][1]) - (wall[0][1]*wall[1][0]) + (wall[1][0]*self.pos[1]) - (wall[1][1]*self.pos[0]) + (wall[0][1]*self.pos[0]) - (wall[0][0]*self.pos[1])) 
		if (A2/wall_length) <= self.rad and self.in_wall_box(wall):
			# First we consider an object that is already overlapping the wall.
			self.update_pos_and_vel_using_wall(wall, A2/wall_length)
		else:
			# Second we consider an object with trajectory to overlap between frames.
			next_pos = self.pos + (self.vel*dt + get_unit_vector(self.vel)*self.rad)
			if intersect(wall[0], wall[1], self.pos, next_pos):
				self.use_intersection_to_set_pos_and_vel(next_pos, wall_length, wall)

	def update_pos(self, dt):
		self.pos = self.pos + self.vel*self.movement_ratio*dt
		self.movement_ratio = 1.0

	def check_collision(self, particle):
		if math.dist(self.pos, particle.pos) <= self.rad + particle.rad:
			return True
		return False

	def separate_atom_to_edge(self, atom):
		# If the particles overlap, they need to be separated by the overlap distance.
		particle_dist = math.dist(atom.pos, self.pos)
		overlap_distance = ((self.rad + atom.rad) - particle_dist)
		unit_vector = np.array(((atom.pos[0]-self.pos[0])/particle_dist, (atom.pos[1]-self.pos[1])/particle_dist))
		atom.pos = atom.pos + unit_vector*(overlap_distance/2)
		self.pos = self.pos + -unit_vector*(overlap_distance/2)

	def elastic_collision(self, atom_1, atom_2):
		m1, m2 = atom_1.rad**2, atom_2.rad**2 
		M = m1 + m2
		r1, r2 = atom_1.pos, atom_2.pos
		d = np.linalg.norm(r1 - r2)**2
		v1, v2 = atom_1.vel, atom_2.vel
		u1 = v1 - 2*m2 / M * np.dot(v1-v2, r1-r2) / d * (r1 - r2)
		u2 = v2 - 2*m1 / M * np.dot(v2-v1, r2-r1) / d * (r2 - r1)
		atom_1.vel = u1
		atom_2.vel = u2

	def in_wall_box(self, wall):
		x_min, x_max = min([wall[0][0], wall[1][0]]), max([wall[0][0], wall[1][0]])
		y_min, y_max = min([wall[0][1], wall[1][1]]), max([wall[0][1], wall[1][1]])
		if ((x_min-self.rad<=self.pos[0]<=x_max+self.rad) and (y_min-self.rad<=self.pos[1]<=y_max+self.rad)):
			return True
		return False

	def update_pos_and_vel_using_wall(self, wall, change, point=None):
		wall_unit_normal = get_vector_unit_normal((wall[1][0]-wall[0][0], wall[1][1]-wall[0][1]))
		self.vel = -2*np.dot(self.vel, wall_unit_normal)*wall_unit_normal + self.vel
		if point is not None:
			self.pos = point
		else:
			self.pos = self.pos - (self.rad-change)*wall_unit_normal

	def use_intersection_to_set_pos_and_vel(self, next_pos, wall_length, wall):
		gradient, constant = get_gradient_and_constant(self.pos, next_pos)
		point = self.get_point_touching_wall(wall_length, wall, gradient, constant)
		if point is not None:
			self.update_movement_ratio(next_pos, point)
			self.update_pos_and_vel_using_wall(wall, 0, point)

	def get_point_touching_wall(self, w, wall, m1, c1):
		# If top or bottom is zero this fails so at present is untreated for rapid objects.
		top = (-self.rad*w) - (wall[0][0]*wall[1][1]) + (wall[0][1]*wall[1][0]) - (c1*wall[1][0]) + c1*wall[0][0]
		bottom = (wall[1][0]*m1) - wall[1][1] + wall[0][1] - (wall[0][0]*m1)
		if top != 0 and bottom != 0:
			x = top / bottom
			y = m1*x + c1
			return np.array((x, y))

	def update_movement_ratio(self, next_pos, point):
		dist_to_end = math.dist(self.pos, next_pos)-self.rad
		dist_to_point = math.dist(self.pos, point)
		self.movement_ratio = (dist_to_end - dist_to_point)/dist_to_end

	def remove_self_from(self, particles):
		for i in range(len(particles)-1, -1, -1):
			particle = particles[i]
			if particle == self:
				particles.pop(i)
		return particles

	def chemical_reaction(self, particle, deletion, products):
		deletion.append(self)
		deletion.append(particle)
		self.reacted, particle.reacted = True, True
		vx = np.random.uniform(-1, 1)*5 + self.vel[0]
		vy = np.random.uniform(-1, 1)*5 + self.vel[1]
		products.append(Product((self.pos[0], self.pos[1]), (vx,vy), self.rad+particle.rad))
		return deletion, products


class Fuel(Particle):
	def __init__(self, pos, vel, rad):
		super().__init__(pos, vel, rad)
		self.type = "fuel"
		self.color = (240,240,80)
		self.reacted = False

	def update_particle_collision(self, particles):
		products, deletion = [], []
		# Can pop the reacted particle...
		if not self.reacted:
			for i in range(len(particles)-1, -1, -1):
				particle = particles[i]
				if particle == self:
					particles.pop(i)
				elif particle.type == "oxidizer" and self.check_collision(particle):
					deletion, products = self.chemical_reaction(particle, deletion, products)
					particles.pop(i)
				elif self.check_collision(particle):
					self.separate_atom_to_edge(particle)
					self.elastic_collision(self, particle)
		else:
			particles = self.remove_self_from(particles)
		return particles, products, deletion


class Ox(Particle):
	def __init__(self, pos, vel, rad):
		super().__init__(pos, vel, rad)
		self.type = "oxidizer"
		self.color = (180,180,240)
		self.reacted = False

	def update_particle_collision(self, particles):
		products, deletion = [], []
		if not self.reacted:
			for i in range(len(particles)-1, -1, -1):
				particle = particles[i]
				if particle == self:
					particles.pop(i)
				elif particle.type == "fuel" and self.check_collision(particle):
					deletion, products = self.chemical_reaction(particle, deletion, products)
					particles.pop(i)
				elif self.check_collision(particle):
					self.separate_atom_to_edge(particle)
					self.elastic_collision(self, particle)
		else:
			particles = self.remove_self_from(particles)
		return particles, products, deletion

class Product(Particle):
	def __init__(self, pos, vel, rad):
		super().__init__(pos, vel, rad)
		self.type = "product"
		self.color = (255,200,200)

	def update_particle_collision(self, particles):
		for i in range(len(particles)-1, -1, -1):
			particle = particles[i]
			if particle == self:
				particles.pop(i)
			elif self.check_collision(particle):
				self.separate_atom_to_edge(particle)
				self.elastic_collision(self, particle)
		return particles, [], []