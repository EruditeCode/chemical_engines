"""
A program to explore a basic rocket engine simulator.

Link to Video: https://youtu.be/BdC1E7WP3so

Notes:
This file has been formatted to remove most functional detail
to the support_functions file (imported as sf). This is to give
clarity to the main file and avoid clutter.
"""

import pygame as pg
import support_functions as sf
from basic_1_boundary import barriers_open, barriers_closed

# Reorganise the boundary data as walls.
walls_closed = sf.barriers_to_walls(barriers_closed)
walls_open = sf.barriers_to_walls(barriers_open)

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

	# Variables and Flags
	flags = {"simulate":False, "pulse":False, "valve":True}
	particles = []
	pulse_count = 0
	momentum = 0
	average_exhaust = False

	# Settings
	dt = 0.5
	CHAMBER_TARGET = 100

	while True:
		flags = sf.user_input_manager(flags)

		# Check the pulse status and add additional particles if required.
		if flags['pulse']:
			flags['simulate'] = True
			if pulse_count < 40:
				particles = sf.create_particle(particles, 0.7, -0.9, 152, 415)
				pulse_count += 1
			else:
				flags['pulse'] = False
				pulse_count = 0

		# Check the simulate flag and if there are particles update them.
		if flags['simulate'] and particles:
			particles.sort(key=lambda x: x.pos[0], reverse=False)
			walls = walls_open if flags['valve'] else walls_closed
			sf.collision_manager(particles, walls, dt)
			sf.update_particle_positions(particles, dt)
			particles, momentum = sf.remove_particles_out_of_bounds(particles, momentum)

		# Find number of particles in parts of the engine and update flags.			
		num_particles_in_ = sf.count_particles_in_engine_parts(particles)
		flags['pulse'] = sf.update_pulse_status(num_particles_in_, CHAMBER_TARGET, flags)
		flags['valve'] = sf.update_valve_status(num_particles_in_['injector'], 0)

		# Displaying objects to the screen.
		sf.draw_engine(screen, flags, bg_open, bg_closed)
		sf.draw_particles(screen, particles)
		sf.draw_basic_UI(screen, font_name, flags, particles, momentum, CHAMBER_TARGET, num_particles_in_)

		pg.display.set_caption(str(clock.get_fps()))
		pg.display.update()
		clock.tick(20)


if __name__ == "__main__":
	main()
