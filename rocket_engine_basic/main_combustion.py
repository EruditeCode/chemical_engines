"""
A program to explore a basic rocket engine simulator with combustion.

Link to Video: https://youtu.be/BdC1E7WP3so

Notes:
This file has been formatted to remove most functional detail
to the support_functions file (imported as sf). This is to give
clarity to the main file and avoid clutter.
"""

import pygame as pg
import support_functions as sf
from combustion_boundary import barriers_moderate

# Reorganise the boundary data as walls.
walls = sf.barriers_to_walls(barriers_moderate)

def main():
	pg.init()
	WIDTH, HEIGHT = 900, 600
	screen = pg.display.set_mode((WIDTH, HEIGHT))
	clock = pg.time.Clock()
	font_name = "LCD-U___.ttf"
	
	bg_open = pg.image.load('combustion_moderate.png')
	bg_open = pg.transform.scale(bg_open, (WIDTH, HEIGHT))

	# Variables and Flags
	flags = {"simulate":False, "pulse":False, "fuel_primed":False, "ox_primed":False}
	particles = []
	pulse_count = 0
	momentum = 0

	# Settings
	dt = 0.2
	CHAMBER_TARGET = 0
	total_fuel, wasted_fuel = 0, 0
	total_ox, wasted_ox = 0, 0
	
	while True:
		flags = sf.combustion_user_input_manager(flags) 

		if flags['pulse']:
			flags['simulate'] = True
			if pulse_count < 40:
				if flags['fuel_primed']:
					particles = sf.create_particle(particles, 0.7, -0.9, 152, 415, "Fuel")
					total_fuel += 1
				if flags['ox_primed']:
					particles = sf.create_particle(particles, 0.7, 0.8, 144, 203, "Ox")
					total_ox += 1
				pulse_count += 1
			else:
				flags['pulse'] = False
				pulse_count = 0


		if flags['simulate'] and particles:
			particles.sort(key=lambda x: x.pos[0], reverse=False)
			particles = sf.combustion_collision_manager(particles, walls, dt, True)
			sf.update_particle_positions(particles, dt)
			particles, momentum, wasted_fuel, wasted_ox = sf.combustion_remove_out_of_bounds(particles, momentum, wasted_fuel, wasted_ox)

		# Find number of particles in parts of the engine and update flags.			
		num_particles_in_ = sf.count_particles_in_engine_parts(particles)
		flags['pulse'] = sf.update_pulse_status(num_particles_in_, CHAMBER_TARGET, flags)
		burn_eff = sf.calculated_burn_efficiency(total_ox, total_fuel, wasted_ox, wasted_fuel)

		# Displaying objects to the screen.
		screen.blit(bg_open, (0, 0))
		sf.draw_particles(screen, particles)
		sf.draw_combustion_UI(screen, font_name, flags, particles, burn_eff, momentum, CHAMBER_TARGET, num_particles_in_)

		pg.display.set_caption(str(clock.get_fps()))
		pg.display.update()
		clock.tick(20)


if __name__ == "__main__":
	main()
