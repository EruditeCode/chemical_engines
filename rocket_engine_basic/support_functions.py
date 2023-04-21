import numpy as np

def barriers_to_walls(barriers):
	walls = []
	for barrier in barriers:
		for i in range(len(barrier)-1,-1,-1):
			walls.append([barrier[i], barrier[i-1]])
	return walls
	
def get_overlap_groups(particles, axis=0):
	# Tidy this up!!!
	groups = []
	group = [particles[0]]
	benchmark = particles[0].pos[axis] + particles[0].rad
	for i in range(1, len(particles)):
		if particles[i].pos[axis]-particles[i].rad <= benchmark:
			group.append(particles[i])
			if particles[i].pos[axis] + particles[i].rad > benchmark:
				benchmark = particles[i].pos[axis] + particles[i].rad
		else:
			groups.append(group.copy())
			group = [particles[i]]
			benchmark = particles[i].pos[axis] + particles[i].rad
	groups.append(group)
	return groups

# Need to improve this to add an actual collision check...
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
