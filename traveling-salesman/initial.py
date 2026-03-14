import numpy as np

def run_tsp(cities):
    """
    Simple baseline for TSP: return the cities in the order they were generated.
    This corresponds to the identity permutation [0, 1, 2, ..., n-1].
    """
    n = len(cities)
    tour = list(range(n))
    return tour
