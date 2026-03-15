import numpy as np
from numba import njit

@njit
def dist(c1, c2):
    return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

@njit
def total_dist(cities, tour):
    d = 0.0
    n = len(tour)
    for i in range(n):
        d += dist(cities[tour[i]], cities[tour[(i+1)%n]])
    return d

@njit
def three_opt_local_search(cities, tour):
    n = len(cities)
    best_tour = tour.copy()
    improved = True
    
    while improved:
        improved = False
        for i in range(n - 2):
            for j in range(i + 1, n - 1):
                for k in range(j + 1, n):
                    # Current edges: (i, i+1), (j, j+1), (k, k+1)
                    A, B = best_tour[i], best_tour[i+1]
                    C, D = best_tour[j], best_tour[j+1]
                    E, F = best_tour[k], best_tour[(k+1)%n]
                    
                    d_base = dist(cities[A], cities[B]) + dist(cities[C], cities[D]) + dist(cities[E], cities[F])
                    
                    # 7 possible reconnections in 3-opt (including 3 2-opts)
                    # Case 1: 2-opt (A-C, B-D, E-F) - reverse [i+1, j]
                    d1 = dist(cities[A], cities[C]) + dist(cities[B], cities[D]) + dist(cities[E], cities[F])
                    if d1 < d_base - 1e-9:
                        best_tour[i+1:j+1] = best_tour[i+1:j+1][::-1]
                        improved = True; break
                        
                    # Case 2: 2-opt (A-B, C-E, D-F) - reverse [j+1, k]
                    d2 = dist(cities[A], cities[B]) + dist(cities[C], cities[E]) + dist(cities[D], cities[F])
                    if d2 < d_base - 1e-9:
                        best_tour[j+1:k+1] = best_tour[j+1:k+1][::-1]
                        improved = True; break
                        
                    # Case 3: 2-opt (A-E, B-D, C-F) - complex reverse
                    d3 = dist(cities[A], cities[E]) + dist(cities[C], cities[D]) + dist(cities[B], cities[F])
                    if d3 < d_base - 1e-9:
                        best_tour[i+1:k+1] = best_tour[i+1:k+1][::-1]
                        improved = True; break
                        
                    # Case 4: 3-opt (A-C, B-E, D-F)
                    d4 = dist(cities[A], cities[C]) + dist(cities[B], cities[E]) + dist(cities[D], cities[F])
                    if d4 < d_base - 1e-9:
                        tmp = np.concatenate((best_tour[:i+1], best_tour[i+1:j+1][::-1], best_tour[j+1:k+1][::-1], best_tour[k+1:]))
                        best_tour = tmp
                        improved = True; break
                        
                    # Case 5: 3-opt (A-D, E-B, C-F)
                    d5 = dist(cities[A], cities[D]) + dist(cities[E], cities[B]) + dist(cities[C], cities[F])
                    if d5 < d_base - 1e-9:
                        tmp = np.concatenate((best_tour[:i+1], best_tour[j+1:k+1], best_tour[i+1:j+1], best_tour[k+1:]))
                        best_tour = tmp
                        improved = True; break
                        
                    # Case 6: 3-opt (A-D, E-C, B-F)
                    d6 = dist(cities[A], cities[D]) + dist(cities[E], cities[C]) + dist(cities[B], cities[F])
                    if d6 < d_base - 1e-9:
                        tmp = np.concatenate((best_tour[:i+1], best_tour[j+1:k+1], best_tour[i+1:j+1][::-1], best_tour[k+1:]))
                        best_tour = tmp
                        improved = True; break
                        
                    # Case 7: 3-opt (A-E, D-B, C-F)
                    d7 = dist(cities[A], cities[E]) + dist(cities[D], cities[B]) + dist(cities[C], cities[F])
                    if d7 < d_base - 1e-9:
                        tmp = np.concatenate((best_tour[:i+1], best_tour[j+1:k+1][::-1], best_tour[i+1:j+1], best_tour[k+1:]))
                        best_tour = tmp
                        improved = True; break
                if improved: break
            if improved: break
            
    return best_tour

@njit
def nearest_neighbor(cities, start_city):
    n = len(cities)
    visited = np.zeros(n, dtype=np.bool_)
    tour = np.zeros(n, dtype=np.int32)
    current = start_city
    tour[0] = current
    visited[current] = True
    for i in range(1, n):
        best_d = np.inf
        best_c = -1
        for next_c in range(n):
            if not visited[next_c]:
                d2 = (cities[current,0]-cities[next_c,0])**2 + (cities[current,1]-cities[next_c,1])**2
                if d2 < best_d:
                    best_d = d2
                    best_c = next_c
        tour[i] = best_c
        visited[best_c] = True
        current = best_c
    return tour

@njit
def solve_tsp(cities):
    n = len(cities)
    best_overall_d = np.inf
    best_overall_tour = np.zeros(n, dtype=np.int32)
    
    # Use all cities as starting points for NN + 3-opt
    for s in range(n):
        initial_tour = nearest_neighbor(cities, s)
        tour = three_opt_local_search(cities, initial_tour)
        d = total_dist(cities, tour)
        if d < best_overall_d:
            best_overall_d = d
            best_overall_tour = tour
            
    return best_overall_tour

def run_tsp(cities):
    """
    Final optimized TSP solution using Multi-Start Nearest Neighbor 
    followed by full 3-opt local search, all accelerated with Numba.
    """
    cities = np.ascontiguousarray(cities, dtype=np.float64)
    tour = solve_tsp(cities)
    return tour.tolist()
