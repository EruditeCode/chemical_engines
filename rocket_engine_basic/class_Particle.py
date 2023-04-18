import math
import numpy as np

class Particle:
	def __init__(self, pos, vel, rad):
		self.pos = np.array((pos[0], pos[1]))
		self.vel = np.array((vel[0], vel[1]))
		self.rad = rad

	def update_interactions(self, walls, atoms=None):
		self.boundary_collision(walls)
		
		# Can alter this logic to be first
		# checking if same atom then checking if in local area...
		# only if it is inside local area do we check for particle_collision...
		if atoms:
			for i in range(len(atoms)-1, -1, -1):
				atom = atoms[i]
				if atom == self:
					atoms.pop(i)
				else:
					if self.particle_collision_check(atom):
						#Make sure each particle is outside the other...
						self.separate_atom_to_edge(atom)
						self.elastic_collision(self, atom)
		return atoms

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

	def separate_atom_to_edge(self, atom):
		# This points from self to the atom...
		ratio = ((atom.rad+self.rad)-(math.dist(atom.pos, self.pos))) / (atom.rad+self.rad)
		vector = np.array(((atom.pos[0]-self.pos[0])/2, (atom.pos[1]-self.pos[1])/2))
		atom.pos = atom.pos + vector*ratio
		self.pos = self.pos + (-vector)*ratio

	def boundary_collision(self, walls):
		for wall in walls:
			if ((max([wall[0][0], wall[1][0]]) + self.rad >= self.pos[0] >= min([wall[0][0], wall[1][0]]) - self.rad) and
				(max([wall[0][1], wall[1][1]]) + self.rad >= self.pos[1] >= min([wall[0][1], wall[1][1]])- self.rad)):
				w = math.dist(wall[0], wall[1])
				A2 = abs((wall[0][0]*wall[1][1]) - (wall[0][1]*wall[1][0]) + (wall[1][0]*self.pos[1]) - (wall[1][1]*self.pos[0]) + (wall[0][1]*self.pos[0]) - (wall[0][0]*self.pos[1])) 
				if (A2 / w) < self.rad:
					#Collision Happened.
					#Set the particle inside the wall.
					wall_vector = (wall[1][0]-wall[0][0], wall[1][1]-wall[0][1])
					wall_normal = (-wall_vector[1], wall_vector[0])
					wall_normal_length = (wall_normal[0]**2 + wall_normal[1]**2)**0.5
					wall_unit_normal = np.array((wall_normal[0]/wall_normal_length, wall_normal[1]/wall_normal_length))
					self.pos = self.pos - (A2 / w)*wall_unit_normal
					# Update the velocity of the particle.
					new_velocity = -2*np.dot(self.vel, wall_unit_normal)*wall_unit_normal + self.vel
					self.vel = new_velocity

	def particle_collision_check(self, particle):
		return math.dist(self.pos, particle.pos) <= self.rad + particle.rad

	def update_pos(self, dt):
		self.pos = self.pos + self.vel * dt