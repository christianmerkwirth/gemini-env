import numpy as np
from numba import njit

@njit
def calculate_dist_sq(c1, c2):
    """Calculates squared Euclidean distance."""
    return (c1[0] - c2[0])**2 + (c1[1] - c2[1])**2

@njit
def nearest_neighbor(cities):
    """
    Finds a tour using the Nearest Neighbor heuristic starting from city 0.
    """
    n = len(cities)
    visited = np.zeros(n, dtype=np.bool_)
    tour = np.zeros(n, dtype=np.int32)
    
    current_city = 0
    tour[0] = current_city
    visited[current_city] = True
    
    for i in range(1, n):
        nearest_city = -1
        min_dist_sq = np.inf
        
        for next_city in range(n):
            if not visited[next_city]:
                d2 = calculate_dist_sq(cities[current_city], cities[next_city])
                if d2 < min_dist_sq:
                    min_dist_sq = d2
                    nearest_city = next_city
        
        tour[i] = nearest_city
        visited[nearest_city] = True
        current_city = nearest_city
        
    return tour

def run_tsp(cities):
    """
    Entry point for the TSP solver.
    Uses a Nearest Neighbor heuristic optimized with numba.
    """
    # Convert cities to a float64 array if it's not already
    cities = np.ascontiguousarray(cities, dtype=np.float64)
    tour = nearest_neighbor(cities)
    return tour.tolist()
