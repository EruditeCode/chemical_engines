"""
A program to explore basic 3D matrix transformations.

Link to Video:
"""

import pygame as pg
import numpy as np
from random import randint
from basic_1_boundary import barriers_open, barriers_closed
from class_Particle import Particle
from support_functions import barriers_to_walls, get_overlap_groups

# Reorganise the boundary data as walls.
walls_closed = barriers_to_walls(barriers_closed)
walls_open = barriers_to_walls(barriers_open)

def main():
	pg.init()
	WIDTH, HEIGHT = 900, 600
	screen = pg.display.set_mode((WIDTH, HEIGHT))
	clock = pg.time.Clock()
	font_name = "LCD-U___.ttf"
	
	bg_open = pg.image.load('basic_1.png')
	bg_open = pg.transform.scale(bg_open, (WIDTH, HEIGHT))
	bg_closed = pg.image.load('basic_1_closed.png')
	bg_closed = pg.transform.scale(bg_closed, (WIDTH, HEIGHT))

	particles = []

	# Flags and Settings
	dt = 0.5
	simulate, pulse, valve = False, False, True
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

		if pulse:
			if pulse_count % 2 == 0:
				vx = np.random.uniform(0.5, 0.9)
				vy = np.random.uniform(-1.0, -0.8)
				x, y = 152, randint(405, 425)
				particles.append(Particle((x, y), (vx,vy), 1))
			pulse_count += 1

			if pulse_count == 100:
				pulse = False
				pulse_count = 0

		if simulate:
			walls = walls_open if valve else walls_closed
			# IMPROVE COLLISION METHOD
			# IMPROVE COLLISION EFFICIENCY
			# IMPROVE COLLISION BOUNDARY EFFICIENCY
			# Update particles in the engine.
			# Take all particles and order them by the x-axis
			particles.sort(key=lambda x: x.pos[0], reverse=False)
			overlap_groups = get_overlap_groups(particles)
			for group in overlap_groups:
				if len(group) == 1:
					group[0].update_interactions(walls)
				else:
					available_atoms = group.copy()
					while available_atoms:
						available_atoms = available_atoms[0].update_interactions(walls, available_atoms)

			for atom in particles:
				atom.update_pos(dt)

			for i in range(len(particles)-1, -1, -1):
				if particles[i].pos[0] > 756:
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
			pg.draw.circle(screen, (240,240,20), particle.pos, particle.rad)

		# Calculating values for text section.
		number_in_injector = 0
		number_in_chamber = 0
		number_in_exhaust = 0
		for particle in particles:
			if particle.pos[0] <= 189:
				number_in_injector += 1
			elif 189 < particle.pos[0] <= 587:
				number_in_chamber += 1
			elif particle.pos[0] > 587:
				number_in_exhaust += 1

		# Displaying information.
		draw_text(screen, font_name, "Basic Rocket Engine", 40, 50, 50, (255,255,255))
		draw_text(screen, font_name, f"Total Particles: {len(particles)}", 20, 50, 95, (240,240,20))
		
		draw_text(screen, font_name, "Injector", 20, 120, 470, (255,255,255))
		if valve:
			draw_text(screen, font_name, "Open", 20, 120, 500, (40, 240, 40))
		else:
			draw_text(screen, font_name, "Closed", 20, 120, 500, (240, 40, 40))
		draw_text(screen, font_name, f"{number_in_injector:0>3}", 20, 120, 530, (240,240,20))
		
		draw_text(screen, font_name, "Chamber", 20, 340, 470, (255,255,255))
		draw_text(screen, font_name, f"{number_in_chamber:0>3}", 20, 340, 500, (240,240,20))
		
		draw_text(screen, font_name, "Exhaust", 20, 620, 470, (255,255,255))
		draw_text(screen, font_name, f"{number_in_exhaust:0>3}", 20, 620, 500, (240,240,20))	

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
