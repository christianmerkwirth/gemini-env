import matplotlib.pyplot as plt
import numpy as np
import best_solution

def plot_packing(n, ax):
    centers, radii, sum_r = best_solution.run_packing(n)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.set_title(f"n={n}, sum_r={sum_r:.4f}")
    
    # Draw unit square boundary
    square = plt.Rectangle((0, 0), 1, 1, fill=False, color='black', linewidth=2)
    ax.add_patch(square)
    
    for i in range(n):
        circle = plt.Circle(centers[i], radii[i], color='blue', alpha=0.3, ec='black')
        ax.add_patch(circle)
        ax.text(centers[i][0], centers[i][1], str(i), fontsize=8, ha='center', va='center')

def main():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    plot_packing(10, axes[0])
    plot_packing(20, axes[1])
    plot_packing(30, axes[2])
    
    plt.tight_layout()
    plt.savefig("best_packings_viz.png")
    print("Visualization saved to best_packings_viz.png")

if __name__ == "__main__":
    main()
