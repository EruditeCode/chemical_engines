import numpy as np

def barriers_to_walls(barriers):
	walls = []
	for barrier in barriers:
		for i in range(len(barrier)-1,-1,-1):
			walls.append([barrier[i], barrier[i-1]])
	return walls

def get_overlap_groups(particles, axis=0):
	groups = []
	group = [particles[0]] 
	for i in range(1, len(particles)):
		if particles[i].pos[axis] <= group[0].pos[axis]+group[0].rad+particles[i].rad:
			group.append(particles[i])
		else:
			groups.append(group.copy())
			group = [particles[i]]
	groups.append(group)
	return groups

def sweep_and_prune(particles):
	# Sort by x-axis.
	x_sorted = get_overlap_groups(particles)
	collision_groups = []
	for group in x_sorted:
		if len(group) > 1:
			# Sort by y-axis
			group.sort(key=lambda x: x.pos[1], reverse=False)
			y_sorted = get_overlap_groups(group, 1)
			for collision in y_sorted:
				if len(collision) > 1:
					collision_groups.append(collision)
	return collision_groups
