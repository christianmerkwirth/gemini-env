import os
import numpy as np
import importlib.util
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import sys

def draw_packing(ax, centers, radii, n):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for center, radius in zip(centers, radii):
        circle = Circle(center, radius, alpha=0.6, facecolor='royalblue', edgecolor='darkblue', linewidth=0.5)
        ax.add_patch(circle)
    sum_radii = np.sum(radii)
    ax.set_title(f"n={n}\nsum={sum_radii:.3f}", fontsize=10)

def main():
    elite_dir = os.path.dirname(os.path.abspath(__file__))
    # Identify unique solutions by looking at data files or py files
    # To avoid redundancy, we only visualize the one with data_20260314.npz if it exists
    py_files = sorted([f for f in os.listdir(elite_dir) if f.endswith('.py') and f != 'evaluate_and_visualize_elite.py'])
    
    print(f"Found {len(py_files)} elite solutions: {py_files}")
    
    for py_file in py_files:
        module_name = py_file[:-3]
        file_path = os.path.join(elite_dir, py_file)
        
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'run_packing'):
            continue
            
        print(f"Evaluating and visualizing {py_file}...")
        # Use 3 rows and 7 columns for 21 packings (n=10..30)
        fig, axes = plt.subplots(3, 7, figsize=(21, 9))
        fig.suptitle(f"Elite Solution: {py_file}", fontsize=20, y=1.05)
        axes = axes.flatten()
        
        total_score = 0
        for i, n in enumerate(range(10, 31)):
            try:
                centers, radii, sum_radii = module.run_packing(n)
                total_score += sum_radii
                draw_packing(axes[i], centers, radii, n)
            except Exception as e:
                axes[i].text(0.5, 0.5, f"Failed n={n}\n{e}", ha='center', va='center')
                print(f"  n={n}: Failed: {e}")
                
        plt.tight_layout()
        output_path = os.path.join(elite_dir, f"summary_{module_name}.png")
        plt.savefig(output_path, bbox_inches="tight", dpi=120)
        plt.close(fig)
        print(f"  Total Score: {total_score:.4f}")
        print(f"  Summary visualization saved to {output_path}")

if __name__ == "__main__":
    main()
