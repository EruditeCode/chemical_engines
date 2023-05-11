import numpy as np

"""
Series of helper functions for matrix/vector transformations.
"""

def get_vector_length(vector):
	return (vector[0]**2 + vector[1]**2)**0.5

def get_vector_normal(vector):
	return (-vector[1], vector[0])

def get_unit_vector(vector):
	length = get_vector_length(vector)
	return np.array((vector[0]/length, vector[1]/length))

def get_vector_unit_normal(vector):
	normal = get_vector_normal(vector)
	return get_unit_vector(normal)


"""
Series of helper functions for line manipulations.
"""

def get_gradient_and_constant(pos_a, pos_b):
	# Needs checking as if x1 = x2 then m = 0 but if y1 = y2 then m = inf.
	if pos_b[1] != pos_a[1] and pos_b[0] != pos_a[0]:
		gradient = (pos_b[1]-pos_a[1])/(pos_b[0]-pos_a[0])
	else:
		gradient = 0
	constant = pos_a[1] - (gradient * pos_a[0])
	return gradient, constant

def ccw(A, B, C):
	return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
