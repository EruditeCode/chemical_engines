import numpy as np
import pygame as pg
from random import randint
from class_Particle import Particle

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

def update_valve_status(number_in_injector, value):
	if number_in_injector <= value:
		return False
	return True

def update_pulse_status(num_particles_in_, CHAMBER_TARGET, flags):
	particles_in_system = num_particles_in_['chamber'] + num_particles_in_['injector']
	if particles_in_system <= CHAMBER_TARGET-30 and not flags['pulse']:
		return True

	if flags['pulse']:
		return True
	return False

def user_input_manager(flags):
	for event in pg.event.get():
		if event.type == pg.QUIT:
			pg.quit()
			exit()
		if event.type == pg.MOUSEBUTTONUP:
			if event.button == 1:
				flags['simulate'] = not flags['simulate']
			if event.button == 3:
				flags['pulse'] = not flags['pulse']
		if event.type == pg.KEYUP:
			if event.key == pg.K_v:
				flags['valve'] = not flags['valve']
	return flags

def create_particle(particles, x_m, y_m, pos_x, pos_y):
	vx = np.random.uniform(x_m-0.2, x_m+0.2)
	vy = np.random.uniform(y_m-0.1, y_m+0.1)
	x, y = 152, randint(pos_y-10, pos_y+10)
	particles.append(Particle((x, y), (vx,vy), 1))
	return particles

def collision_manager(particles, walls, dt):
	# Sweep and prune algorithm to manage collision between particles.
	collision_set = sweep_and_prune(particles)
	for collision_group in collision_set:
		while len(collision_group) > 1:
			collision_group = collision_group[0].update_particle_collision(collision_group)

	# Ignore particles that are not close to a wall.
	particles_close_to_walls = [p for p in particles if ((210>p.pos[0] or p.pos[0]>540) or (220>p.pos[1] or p.pos[1]>375))]
	for wall in walls:
		x_min, x_max = min([wall[0][0], wall[1][0]]), max([wall[0][0], wall[1][0]])
		y_min, y_max = min([wall[0][1], wall[1][1]]), max([wall[0][1], wall[1][1]])
		for p in particles_close_to_walls:
			if ((x_min-p.rad<=p.pos[0]<=x_max+p.rad) and (y_min-p.rad<=p.pos[1]<=y_max+p.rad)):
				# At present the update wall doesn't perform continuous calc...
				p.update_wall_collision(wall, dt)

def update_particle_positions(particles, dt):
	for particle in particles:
		particle.update_pos(dt)

def remove_particles_out_of_bounds(particles, momentum):
	for i in range(len(particles)-1, -1, -1):
		if particles[i].pos[0] > 760:
			momentum += particles[i].vel[0]*particles[i].rad
			particles.pop(i)
		elif (particles[i].pos[1] > 500 or particles[i].pos[1] < 100):
			particles.pop(i)
	return particles, momentum

def count_particles_in_engine_parts(particles):
	injector, chamber = 0, 0
	for particle in particles:
		if particle.pos[0] <= 198:
			injector += 1
		elif 198 < particle.pos[0] <= 587:
			chamber += 1
	return {'injector':injector, 'chamber':chamber}

def draw_engine(screen, flags, bg_open, bg_closed):
	if flags['valve']:
		screen.blit(bg_open, (0, 0))
	else:
		screen.blit(bg_closed, (0, 0))

def draw_particles(screen, particles):
	for particle in particles:
		pg.draw.circle(screen, (240,240,20), particle.pos, particle.rad)

def draw_text(screen, font_name, text, size, x, y, color):
	font = pg.font.Font(font_name, size)
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	text_rect.topleft = (x, y)
	screen.blit(text_surface, text_rect)

def draw_basic_UI(screen, font_name, flags, particles, momentum, CHAMBER_TARGET, num_particles_in_):
	draw_text(screen, font_name, "Basic Rocket Engine", 40, 50, 50, (255,255,255))
	draw_text(screen, font_name, f"Total Particles: {len(particles)}", 20, 50, 95, (240,240,20))
	draw_text(screen, font_name, f"Chamber Target: {CHAMBER_TARGET}", 20, 50, 125, (240,240,20))
	
	draw_text(screen, font_name, "Injector", 20, 120, 470, (255,255,255))
	if flags['valve']:
		draw_text(screen, font_name, "Open", 20, 120, 500, (40, 240, 40))
	else:
		draw_text(screen, font_name, "Closed", 20, 120, 500, (240, 40, 40))
	draw_text(screen, font_name, f"{num_particles_in_['injector']:0>3}", 20, 120, 530, (240,240,20))
	
	draw_text(screen, font_name, "Chamber", 20, 340, 470, (255,255,255))
	draw_text(screen, font_name, f"{num_particles_in_['chamber']:0>3}", 20, 340, 500, (240,240,20))
	
	draw_text(screen, font_name, "Exhaust", 20, 620, 470, (255,255,255))
	draw_text(screen, font_name, f"Momentum: {int(momentum):0>5}", 20, 620, 500, (255,255,255))
