import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import os

def visualize(centers, radii, output_path):
    """
    Visualize the circle packing and save to PNG.
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Draw unit square
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.grid(True, linestyle='--', alpha=0.6)

    # Draw circles
    for i, (center, radius) in enumerate(zip(centers, radii)):
        circle = Circle(center, radius, alpha=0.5, color='royalblue', edgecolor='darkblue')
        ax.add_patch(circle)
        ax.text(center[0], center[1], str(i), ha="center", va="center", fontsize=8, fontweight='bold')

    sum_radii = np.sum(radii)
    ax.set_title(f"Circle Packing (n={len(centers)}, sum={sum_radii:.6f})", fontsize=16)
    
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close(fig)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    # Load the best result
    data_path = "run_20260308_123245/results/gen_200_final/extra.npz"
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
    else:
        data = np.load(data_path)
        centers = data['centers']
        radii = data['radii']
        
        output_png = "best_circle_packing.png"
        visualize(centers, radii, output_png)
