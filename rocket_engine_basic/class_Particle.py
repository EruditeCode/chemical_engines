import math
import numpy as np

def ccw(A, B, C):
	return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Particle:
	def __init__(self, pos, vel, rad):
		self.pos = np.array((pos[0], pos[1]))
		self.vel = np.array((vel[0], vel[1]))
		self.rad = rad
		self.movement_ratio = 1.0

	def update_particle_collision(self, particles):
		for i in range(len(particles)-1, -1, -1):
			particle = particles[i]
			if particle == self:
				particles.pop(i)
			else:
				self.separate_atom_to_edge(particle)
				self.elastic_collision(self, particle)
		return particles

	def update_wall_collision(self, wall, dt):
		self.boundary_collision(wall, dt)

	def update_pos(self, dt):
		self.pos = self.pos + self.vel*self.movement_ratio*dt
		self.movement_ratio = 1.0

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

	def boundary_collision(self, wall, dt):
		w = math.dist(wall[0], wall[1])
		A2 = abs((wall[0][0]*wall[1][1]) - (wall[0][1]*wall[1][0]) + (wall[1][0]*self.pos[1]) - (wall[1][1]*self.pos[0]) + (wall[0][1]*self.pos[0]) - (wall[0][0]*self.pos[1])) 
		if (A2 / w) <= self.rad:
			# Collision has already happened within this frame.
			# Set the particle inside the wall.
			wall_vector = (wall[1][0]-wall[0][0], wall[1][1]-wall[0][1])
			wall_normal = (-wall_vector[1], wall_vector[0])
			wall_normal_length = (wall_normal[0]**2 + wall_normal[1]**2)**0.5
			wall_unit_normal = np.array((wall_normal[0]/wall_normal_length, wall_normal[1]/wall_normal_length))
			self.pos = self.pos - (self.rad-(A2 / w))*wall_unit_normal
			# Update the velocity of the particle.
			new_velocity = -2*np.dot(self.vel, wall_unit_normal)*wall_unit_normal + self.vel
			self.vel = new_velocity
		# else:
		# 	# THIS SECTION NEEDS SOME SERIOUS WORK!!!
		# 	# Check if heading towards the wall, are we likely to miss the collision?
		# 	temp_point = self.pos + self.vel*dt
		# 	if intersect(wall[0], wall[1], self.pos, temp_point):
		# 		print("INTERSECTION")
		# 		# Equation for particle line (gradient - m1, constant - c1)
		# 		if temp_point[1] != self.pos[1] and temp_point[0] != self.pos[0]:
		# 			m1 = (temp_point[1]-self.pos[1])/(temp_point[0]-self.pos[0])
		# 		else:
		# 			m1 = 0
		# 		c1 = self.pos[1] - (m1 * self.pos[0])

		# 		top = (self.rad*w) - (wall[0][0]*wall[1][1]) + (wall[0][1]*wall[1][0]) - (c1*wall[1][0]) + c1*wall[0][0]
		# 		bottom = (wall[1][0]*m1) - wall[1][1] + wall[0][1] - (wall[0][0]*m1)
		# 		x = top / bottom
		# 		y = m1*x + c1
		# 		point = np.array((x, y))
		# 		#print(point)
		# 		dist_to_end = math.dist(self.pos, temp_point)
		# 		dist_to_point = math.dist(self.pos, point)
		# 		#print(dist_to_end)
		# 		#print(dist_to_point)
		# 		#print("HELP")
		# 		move_particle = dist_to_point/dist_to_end
		# 		self.pos = point
		# 		self.movement_ratio = 1 - move_particle

		# 		wall_vector = (wall[1][0]-wall[0][0], wall[1][1]-wall[0][1])
		# 		wall_normal = (-wall_vector[1], wall_vector[0])
		# 		wall_normal_length = (wall_normal[0]**2 + wall_normal[1]**2)**0.5
		# 		wall_unit_normal = np.array((wall_normal[0]/wall_normal_length, wall_normal[1]/wall_normal_length))
		# 		new_velocity = -2*np.dot(self.vel, wall_unit_normal)*wall_unit_normal + self.vel
		# 		self.vel = new_velocity

