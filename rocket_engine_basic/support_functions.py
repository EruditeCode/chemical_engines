

def barriers_to_walls(barriers):
	walls = []
	for barrier in barriers:
		for i in range(len(barrier)):
			walls.append([barrier[i-1], barrier[i]])
	return walls

def get_overlap_groups(particles):
	groups = []
	group = [particles[0]] 
	for i in range(1, len(particles)):
		if particles[i].pos[0] < group[0].pos[0]+2:
			group.append(particles[i])
		else:
			groups.append(group.copy())
			group = [particles[i]]
	groups.append(group)
	return groups