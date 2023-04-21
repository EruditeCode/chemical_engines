"""
A program to explore a basic rocket engine simulator with combustion.

Link to Video:
"""

import pygame as pg
from class_Particle import Particle, Fuel, Ox, Product
from support_functions import barriers_to_walls, sweep_and_prune

# Reorganise the boundary data as walls.
barriers = [[(0,0), (900,0), (900, 600), (0,600)]]
walls_open = barriers_to_walls(barriers)

def main():
	pg.init()
	WIDTH, HEIGHT = 900, 600
	screen = pg.display.set_mode((WIDTH, HEIGHT))
	clock = pg.time.Clock()
	
	bg = pg.Surface((WIDTH, HEIGHT))
	bg.fill((20,20,20))

	particles = [Fuel((100, 300), (2.9, -3.1), 40), Fuel((500, 400), (-2.5, 4.1), 40),
				Fuel((40, 50), (1.9, 2.1), 40), Fuel((550, 50), (-1.5, -4.1), 40),
				Fuel((80, 500), (4.9, -0.6), 40), Fuel((600, 200), (2.5, 3.1), 40),
				]

	# particles = [Fuel((100, 300), (0, 0), 40), Fuel((130, 310), (0, 0), 40)]

	# Flags and Settings
	dt = 0.5
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
			# Sweep and prune algorithm to manage collision between particles.
			particles.sort(key=lambda x: x.pos[0], reverse=False)
			collision_set = sweep_and_prune(particles)
			deletable, new = [], []
			# print(collision_set)
			for collision_group in collision_set:
				while len(collision_group) > 1:
					print(collision_group)
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

			# Select walls dependent on valve status.
			walls = walls_open
			# Ignore particles that are not close to a wall.
			particles_close_to_walls = [p for p in particles if ((210>p.pos[0] or p.pos[0]>540) or (220>p.pos[1] or p.pos[1]>375))]
			for wall in walls:
				x_min, x_max = min([wall[0][0], wall[1][0]]), max([wall[0][0], wall[1][0]])
				y_min, y_max = min([wall[0][1], wall[1][1]]), max([wall[0][1], wall[1][1]])
				for p in particles_close_to_walls:
					if ((x_min-p.rad<=p.pos[0]<=x_max+p.rad) and (y_min-p.rad<=p.pos[1]<=y_max+p.rad)):
						# At present the update wall doesn't perform continuous calc...
						p.update_wall_collision(wall, dt)

			# Update particle positions.
			for atom in particles:
				atom.update_pos(dt)

		# Displaying the background.
		screen.blit(bg, (0, 0))

		# Displaying the particles.
		for particle in particles:
			pg.draw.circle(screen, particle.color, particle.pos, particle.rad)

		pg.display.set_caption(str(clock.get_fps()))
		pg.display.update()
		clock.tick(60)

if __name__ == "__main__":
	main()
