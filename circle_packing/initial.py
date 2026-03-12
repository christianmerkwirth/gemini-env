# EVOLVE-BLOCK-START
"""Constructor-based circle packing for n=26 circles"""

import numpy as np


def construct_packing(n=26):
    """
    Construct a specific arrangement of n circles in a unit square
    that attempts to maximize the sum of their radii.

    Args:
        n: Number of circles to place

    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (n, 2) with (x, y) coordinates
        radii: np.array of shape (n) with radius of each circle
    """
    # Initialize arrays for n circles
    centers = np.zeros((n, 2))

    # Place circles in a structured pattern
    # This is a simple pattern - evolution will improve this

    # First, place a large circle in the center
    if n > 0:
        centers[0] = [0.5, 0.5]

    if n > 1:
        # Divide remaining circles into two rings if possible
        n_inner = min(8, n - 1)
        n_outer = n - 1 - n_inner

        # Place circles in an inner ring
        for i in range(n_inner):
            angle = 2 * np.pi * i / n_inner
            centers[i + 1] = [0.5 + 0.25 * np.cos(angle), 0.5 + 0.25 * np.sin(angle)]

        # Place remaining circles in an outer ring
        for i in range(n_outer):
            angle = 2 * np.pi * i / n_outer if n_outer > 0 else 0
            centers[i + 1 + n_inner] = [0.5 + 0.45 * np.cos(angle), 0.5 + 0.45 * np.sin(angle)]

    # Additional positioning adjustment to make sure all circles
    # are inside the square and don't overlap
    # Clip to ensure everything is inside the unit square
    centers = np.clip(centers, 0.01, 0.99)

    # Compute maximum valid radii for this configuration
    radii = compute_max_radii(centers)
    return centers, radii


def compute_max_radii(centers):
    """
    Compute the maximum possible radii for each circle position
    such that they don't overlap and stay within the unit square.

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates

    Returns:
        np.array of shape (n) with radius of each circle
    """
    n = centers.shape[0]
    radii = np.ones(n)

    # First, limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        # Distance to borders
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Then, limit by distance to other circles
    # Each pair of circles with centers at distance d can have
    # sum of radii at most d to avoid overlap
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))

            # If current radii would cause overlap
            if radii[i] + radii[j] > dist:
                # Scale both radii proportionally
                scale = dist / (radii[i] + radii[j])
                radii[i] *= scale
                radii[j] *= scale

    return radii


# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing(n=26):
    """Run the circle packing constructor for n circles"""
    centers, radii = construct_packing(n)
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
