"""
A program to explore a basic rocket engine simulator with combustion.

Link to Video:
"""

import pygame as pg
import numpy as np
from random import randint
from combustion_boundary import barriers_open
from class_Particle import Particle, Fuel, Ox, Product
from support_functions import barriers_to_walls, sweep_and_prune

# Reorganise the boundary data as walls.
#walls_closed = barriers_to_walls(barriers_closed)
walls_open = barriers_to_walls(barriers_open)

def main():
	pg.init()
	WIDTH, HEIGHT = 900, 600
	screen = pg.display.set_mode((WIDTH, HEIGHT))
	clock = pg.time.Clock()
	font_name = "LCD-U___.ttf"
	
	bg_open = pg.image.load('combustion_open.png')
	bg_open = pg.transform.scale(bg_open, (WIDTH, HEIGHT))
	bg_closed = pg.image.load('combustion_open.png')
	bg_closed = pg.transform.scale(bg_closed, (WIDTH, HEIGHT))

	particles = []
	momentum = 0

	CHAMBER_TARGET = 300
	total_fuel = 0
	wasted_fuel = 0
	total_ox = 0
	wasted_ox = 0

	# Flags and Settings
	dt = 0.2
	simulate, pulse, valve = False, False, True
	fuel_primed, ox_primed = False, False
	pulse_count = 0
	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				exit()
			if event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					simulate = not simulate
				if event.button == 3:
					pulse = not pulse
			if event.type == pg.KEYUP:
				if event.key == pg.K_v:
					valve = not valve
				if event.key == pg.K_f:
					fuel_primed = not fuel_primed
				if event.key == pg.K_o:
					ox_primed = not ox_primed 

		if pulse:
			simulate = True
			if pulse_count % 2 == 0:
				#Fuel
				if fuel_primed:
					vx = np.random.uniform(0.5, 0.9)
					vy = np.random.uniform(-1.0, -0.8)
					x, y = 152, randint(405, 425)
					particles.append(Fuel((x, y), (vx,vy), 1))
					total_fuel += 1

				# Ox
				if ox_primed:
					vx = np.random.uniform(0.5, 0.9)
					vy = np.random.uniform(0.5, 1.0)
					x, y = 144, randint(192, 207)
					particles.append(Ox((x, y), (vx,vy), 1))
					total_ox += 1
			pulse_count += 1

			if pulse_count == 80:
				pulse = False
				pulse_count = 0

		if simulate and particles:
			# Sweep and prune algorithm to manage collision between particles.
			particles.sort(key=lambda x: x.pos[0], reverse=False)
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
					#particles.remove(delete)

			if new:
				for product in new:
					particles.append(product)

			# Select walls dependent on valve status.
			walls = walls_open #if valve else walls_closed
			# Ignore particles that are not close to a wall.
			particles_close_to_walls = [p for p in particles if ((210>p.pos[0] or p.pos[0]>540) or (220>p.pos[1] or p.pos[1]>375))]
			for wall in walls:
				x_min, x_max = min([wall[0][0], wall[1][0]]), max([wall[0][0], wall[1][0]])
				y_min, y_max = min([wall[0][1], wall[1][1]]), max([wall[0][1], wall[1][1]])
				for p in particles_close_to_walls:
					if ((x_min-20<=p.pos[0]<=x_max+20) and (y_min-20<=p.pos[1]<=y_max+20)):
						# At present the update wall doesn't perform continuous calc...
						p.update_wall_collision(wall, dt)

			# Update particle positions.
			for atom in particles:
				atom.update_pos(dt)

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
					print("OOPS")

		# Displaying the engine.
		if valve:
			screen.blit(bg_open, (0, 0))
		else:
			screen.blit(bg_closed, (0, 0))

		# Displaying the particles.
		for particle in particles:
			pg.draw.circle(screen, particle.color, particle.pos, particle.rad)

		# Calculating values for text section.
		number_in_injector = 0
		number_in_chamber = 0
		number_in_exhaust = 0
		for particle in particles:
			if particle.pos[0] <= 198:
				number_in_injector += 1
			elif 198 < particle.pos[0] <= 587:
				number_in_chamber += 1

		# if number_in_chamber + number_in_injector <= CHAMBER_TARGET-30 and not pulse:
		# 	pulse = True
		
		# if number_in_injector == 0:
		# 	valve = False
		# else:
		# 	valve = True

		# Burn efficiency
		if total_ox and total_fuel:
			burn_eff = (1 - (wasted_fuel / total_fuel)) * 100
		else:
			burn_eff = 0

		# Displaying information.
		draw_text(screen, font_name, "Basic Rocket Engine", 40, 50, 50, (255,255,255))
		draw_text(screen, font_name, f"Total Particles: {len(particles)}", 20, 50, 95, (240,240,20))
		draw_text(screen, font_name, f"Combustion Efficiency: {burn_eff:0>3}", 20, 50, 120, (240,240,20))
		
		draw_text(screen, font_name, "Oxid", 20, 30, 210, (255,255,255))	
		if ox_primed:
			draw_text(screen, font_name, "Primed", 20, 30, 240, (40, 240, 40))
		else:
			draw_text(screen, font_name, "Locked", 20, 30, 240, (240, 40, 40))

		draw_text(screen, font_name, "Fuel", 20, 30, 350, (255,255,255))
		if fuel_primed:
			draw_text(screen, font_name, "Primed", 20, 30, 380, (40, 240, 40))
		else:
			draw_text(screen, font_name, "Locked", 20, 30, 380, (240, 40, 40))

		draw_text(screen, font_name, "Injectors", 20, 120, 470, (255,255,255))
		if valve:
			draw_text(screen, font_name, "Open", 20, 120, 500, (40, 240, 40))
		else:
			draw_text(screen, font_name, "Closed", 20, 120, 500, (240, 40, 40))
		draw_text(screen, font_name, f"{number_in_injector:0>3}", 20, 120, 530, (240,240,20))
		
		draw_text(screen, font_name, "Chamber", 20, 340, 470, (255,255,255))
		draw_text(screen, font_name, f"Target: {CHAMBER_TARGET}", 20, 340, 500, (240,240,20))
		draw_text(screen, font_name, f"{number_in_chamber:0>3}", 20, 340, 530, (240,240,20))
		
		draw_text(screen, font_name, "Exhaust", 20, 620, 470, (255,255,255))
		draw_text(screen, font_name, f"Momentum: {int(momentum):0>5}", 20, 620, 500, (240,240,20))

		pg.display.set_caption(str(clock.get_fps()))
		pg.display.update()
		clock.tick(60)

def draw_text(screen, font_name, text, size, x, y, color):
	font = pg.font.Font(font_name, size)
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	text_rect.topleft = (x, y)
	screen.blit(text_surface, text_rect)

if __name__ == "__main__":
	main()
