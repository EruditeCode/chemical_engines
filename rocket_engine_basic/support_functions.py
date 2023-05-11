import numpy as np
import pygame as pg
from random import randint
from class_Particle import Particle, Fuel, Ox

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

def create_particle(particles, x_m, y_m, pos_x, pos_y, p_type=None):
	vx = np.random.uniform(x_m-0.2, x_m+0.2)
	vy = np.random.uniform(y_m-0.1, y_m+0.1)
	x, y = 152, randint(pos_y-7, pos_y+7)
	if p_type == "Fuel":
		particles.append(Fuel((x, y), (vx,vy), 1))
	elif p_type == "Ox":
		particles.append(Ox((x, y), (vx,vy), 1))
	else:
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
		pg.draw.circle(screen, particle.color, particle.pos, particle.rad)

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

def combustion_user_input_manager(flags):
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
			if event.key == pg.K_f:
				flags['fuel_primed'] = not flags['fuel_primed']
			if event.key == pg.K_o:
				flags['ox_primed'] = not flags['ox_primed']
	return flags

def combustion_collision_manager(particles, walls, dt, wide_check=False):
	# Sweep and prune algorithm to manage collision between particles.
	collision_set = sweep_and_prune(particles)
	deletable, new = [], []
	for collision_group in collision_set:
		while len(collision_group) > 1:
			collision_group, products, delete = collision_group[0].update_particle_collision(collision_group)
			deletable.extend(delete)
			new.extend(products)

	if deletable: 
		for delete in deletable:
			for i, particle in enumerate(particles):
				if particle == delete:
					break
			particles.pop(i)

	if new:
		for product in new:
			particles.append(product)

	# Ignore particles that are not close to a wall.
	particles_close_to_walls = [p for p in particles if ((210>p.pos[0] or p.pos[0]>540) or (220>p.pos[1] or p.pos[1]>375))]
	for wall in walls:
		x_min, x_max = min([wall[0][0], wall[1][0]]), max([wall[0][0], wall[1][0]])
		y_min, y_max = min([wall[0][1], wall[1][1]]), max([wall[0][1], wall[1][1]])
		for p in particles_close_to_walls:
			if wide_check:
				if ((x_min-20<=p.pos[0]<=x_max+20) and (y_min-20<=p.pos[1]<=y_max+20)):
					p.update_wall_collision(wall, dt)
			else:
				if ((x_min-p.rad*2<=p.pos[0]<=x_max+p.rad*2) and (y_min-p.rad*2<=p.pos[1]<=y_max+p.rad*2)):
					p.update_wall_collision(wall, dt)
	return particles

def combustion_remove_out_of_bounds(particles, momentum, wasted_fuel, wasted_ox):
	for i in range(len(particles)-1, -1, -1):
		if particles[i].pos[0] > 760:
			momentum += particles[i].vel[0]*particles[i].rad
			if particles[i].type == "fuel":
				wasted_fuel += 1
			elif particles[i].type == "oxidizer":
				wasted_ox += 1
			particles.pop(i)
		elif (particles[i].pos[1] > 500 or particles[i].pos[1] < 100):
			particles.pop(i)
	return particles, momentum, wasted_fuel, wasted_ox

def calculated_burn_efficiency(total_ox, total_fuel, wasted_ox, wasted_fuel):
	if total_ox and total_fuel:
		if total_ox <= total_fuel:
			return (1 - (wasted_ox / total_ox)) * 100
		else:
			return (1 - (wasted_fuel / total_fuel)) * 100
	return 0

def draw_combustion_UI(screen, font_name, flags, particles, burn_eff, momentum, CHAMBER_TARGET, num_particles_in_):
	draw_text(screen, font_name, "Basic Rocket Engine", 40, 50, 50, (255,255,255))
	draw_text(screen, font_name, f"Total Particles: {len(particles)}", 20, 50, 95, (240,240,20))
	draw_text(screen, font_name, f"Combustion Efficiency: {burn_eff:0>3}", 20, 50, 120, (240,240,20))
	
	draw_text(screen, font_name, "Oxid", 20, 30, 210, (255,255,255))	
	if flags["ox_primed"]:
		draw_text(screen, font_name, "Primed", 20, 30, 240, (40, 240, 40))
	else:
		draw_text(screen, font_name, "Locked", 20, 30, 240, (240, 40, 40))

	draw_text(screen, font_name, "Fuel", 20, 30, 350, (255,255,255))
	if flags["fuel_primed"]:
		draw_text(screen, font_name, "Primed", 20, 30, 380, (40, 240, 40))
	else:
		draw_text(screen, font_name, "Locked", 20, 30, 380, (240, 40, 40))

	draw_text(screen, font_name, "Injectors", 20, 120, 470, (255,255,255))
	draw_text(screen, font_name, f"{num_particles_in_['injector']:0>3}", 20, 120, 500, (240,240,20))
	
	draw_text(screen, font_name, "Chamber", 20, 340, 470, (255,255,255))
	draw_text(screen, font_name, f"Target: {CHAMBER_TARGET}", 20, 340, 500, (240,240,20))
	draw_text(screen, font_name, f"{num_particles_in_['chamber']:0>3}", 20, 340, 530, (240,240,20))
	
	draw_text(screen, font_name, "Exhaust", 20, 620, 470, (255,255,255))
	draw_text(screen, font_name, f"Momentum: {int(momentum):0>5}", 20, 620, 500, (240,240,20))
