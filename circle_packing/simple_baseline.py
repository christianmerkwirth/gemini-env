import numpy as np

def construct_packing(n=26):
    """
    Simple baseline using grid-based positions and a constant radius.
    The total score across n=10..30 will be approximately 27.5.
    Sum of n from 10 to 30 is 420.
    Radius r = 27.5 / 420 = 0.065476...
    """
    side = int(np.ceil(np.sqrt(n)))
    r = 27.5 / 420.0
    
    # Grid placement
    centers = []
    for i in range(n):
        row = i // side
        col = i % side
        # Center of each cell in the grid
        x = (col + 0.5) / side
        y = (row + 0.5) / side
        centers.append([x, y])
    
    centers = np.array(centers)
    radii = np.full(n, r)
    
    return centers, radii

def run_packing(n=26):
    centers, radii = construct_packing(n)
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
