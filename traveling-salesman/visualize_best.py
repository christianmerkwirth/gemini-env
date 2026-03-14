import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import importlib.util

def generate_cities(n: int) -> np.ndarray:
    """Generates random city coordinates in [0, 1] x [0, 1]."""
    np.random.seed(42 + n)
    return np.random.rand(n, 2)

def load_solution(program_path: str):
    spec = importlib.util.spec_from_file_location("tsp_module", program_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_tsp

def main():
    best_program = "run_20260314_235703/gen4_v1_ils_optimized.py"
    run_tsp = load_solution(best_program)
    
    fig, axes = plt.subplots(7, 3, figsize=(15, 30))
    axes = axes.flatten()
    
    for idx, n in enumerate(range(20, 41)):
        print(f"Plotting n = {n}...")
        cities = generate_cities(n)
        tour = run_tsp(cities)
        
        ax = axes[idx]
        # Plot edges
        tour_coords = cities[tour + [tour[0]]]
        ax.plot(tour_coords[:, 0], tour_coords[:, 1], 'b-', alpha=0.6)
        # Plot cities
        ax.scatter(cities[:, 0], cities[:, 1], c='red', s=20)
        # Mark start
        ax.scatter(cities[tour[0], 0], cities[tour[0], 1], c='green', s=50, marker='s')
        
        ax.set_title(f"n = {n}")
        ax.set_aspect('equal')
        ax.set_xticks([])
        ax.set_yticks([])

    plt.tight_layout()
    output_path = "best_solution_visualization.png"
    plt.savefig(output_path)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    main()
