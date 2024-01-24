import numpy as np


def create_polynom(x, y, degree):
    coeffs = np.polyfit(x, y, degree)
    return coeffs

