import numpy as np

def barriers_to_walls(barriers):
	walls = []
	for barrier in barriers:
		for i in range(len(barrier)-1,-1,-1):
			walls.append([barrier[i], barrier[i-1]])
	return walls
	
def get_overlap_groups(particles, axis=0):
	# Function to group particles by overlap in a given axis.
	groups, group = [], [particles[0]]
	threshold = particles[0].pos[axis] + particles[0].rad
	for i in range(1, len(particles)):
		if particles[i].pos[axis]-particles[i].rad <= threshold:
			group.append(particles[i])
			if particles[i].pos[axis] + particles[i].rad > threshold:
				threshold = particles[i].pos[axis] + particles[i].rad
		else:
			groups.append(group.copy())
			group = [particles[i]]
			threshold = particles[i].pos[axis] + particles[i].rad
	groups.append(group)
	return groups

def sweep_and_prune(particles):
	# Function to grouping particles by proximity in the x and y axis.
	x_sorted = get_overlap_groups(particles)
	collision_groups = []
	for group in x_sorted:
		if len(group) > 1:
			group.sort(key=lambda x: x.pos[1], reverse=False)
			y_sorted = get_overlap_groups(group, 1)
			for collision in y_sorted:
				if len(collision) > 1:
					collision_groups.append(collision)
	return collision_groups


"""
Series of helper functions for matrix/vector transformations.
"""

def get_vector_length(vector):
	return (vector[0]**2 + vector[1]**2)**0.5

def get_vector_normal(vector):
	return (-vector[1], vector[0])

def get_unit_vector(vector):
	length = get_vector_length(vector)
	return np.array((vector[0]/length, vector[1]/length))

def get_vector_unit_normal(vector):
	normal = get_vector_normal(vector)
	return get_unit_vector(normal)


"""
Series of helper functions for line manipulations.
"""

def get_gradient_and_constant(pos_a, pos_b):
	# Needs checking as if x1 = x2 then m = 0 but if y1 = y2 then m = inf.
	if pos_b[1] != pos_a[1] and pos_b[0] != pos_a[0]:
		gradient = (pos_b[1]-pos_a[1])/(pos_b[0]-pos_a[0])
	else:
		gradient = 0
	constant = pos_a[1] - (gradient * pos_a[0])
	return gradient, constant

def ccw(A, B, C):
	return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
