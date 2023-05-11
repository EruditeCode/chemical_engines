"""
A program to explore a basic collision reaction model.

Link to Video: https://youtu.be/BdC1E7WP3so
"""

import pygame as pg
import support_functions as sf
from class_Particle import Particle, Fuel, Ox, Product

# Reorganise the boundary data as walls.
walls = sf.barriers_to_walls([[(0,0), (900,0), (900, 600), (0,600)]])

def main():
	pg.init()
	WIDTH, HEIGHT = 900, 600
	screen = pg.display.set_mode((WIDTH, HEIGHT))
	clock = pg.time.Clock()
	
	bg = pg.Surface((WIDTH, HEIGHT))
	bg.fill((20,20,20))

	particles = [
				Fuel((100, 300), (2.9, -3.1), 40), Ox((500, 400), (-2.5, 4.1), 40),
				Fuel((45, 50), (1.9, 2.1), 40), Ox((550, 50), (-1.5, -4.1), 40),
				Fuel((80, 500), (4.9, -0.6), 40), Ox((600, 200), (2.5, 3.1), 40),
				]

	# Flags and Settings
	dt = 2
	simulate = False
	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				pg.quit()
				exit()
			if event.type == pg.MOUSEBUTTONUP:
				if event.button == 1:
					simulate = not simulate

		if simulate and particles:
			particles.sort(key=lambda x: x.pos[0], reverse=False)
			particles = sf.combustion_collision_manager(particles, walls, dt)
			sf.update_particle_positions(particles, dt)

		# Displaying objects to the screen.
		screen.blit(bg, (0, 0))
		sf.draw_particles(screen, particles)

		pg.display.set_caption(str(clock.get_fps()))
		pg.display.update()
		clock.tick(60)

if __name__ == "__main__":
	main()
