import os
import argparse
import json
import numpy as np
import multiprocessing
import importlib.util
import sys
from typing import Tuple, Optional, List, Dict, Any

def generate_cities(n: int) -> np.ndarray:
    """Generates random city coordinates in [0, 1] x [0, 1]."""
    np.random.seed(42 + n)
    return np.random.rand(n, 2)

def calculate_distance(cities: np.ndarray, tour: List[int]) -> float:
    """Calculates the total Euclidean distance of a tour."""
    dist = 0.0
    n = len(cities)
    for i in range(n):
        c1 = cities[tour[i]]
        c2 = cities[tour[(i + 1) % n]]
        dist += np.sqrt(np.sum((c1 - c2)**2))
    return dist

def validate_tour(n: int, tour: Any) -> Tuple[bool, str]:
    """Validates that the tour is a valid permutation of city indices."""
    if not isinstance(tour, (list, np.ndarray)):
        return False, f"Tour must be a list or numpy array, got {type(tour)}"
    if len(tour) != n:
        return False, f"Tour length must be {n}, got {len(tour)}"
    
    tour_list = [int(x) for x in tour]
    if sorted(tour_list) != list(range(n)):
        return False, "Tour must be a valid permutation of indices 0 to n-1"
    
    return True, "Valid"

def worker(program_path: str, n: int) -> Tuple[int, Optional[List[int]], float, Optional[str]]:
    """Worker function for parallel execution."""
    try:
        cities = generate_cities(n)
        
        module_name = f"module_{n}_{os.getpid()}"
        spec = importlib.util.spec_from_file_location(module_name, program_path)
        if spec is None or spec.loader is None:
            return n, None, 0.0, f"Could not load module from {program_path}"
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if not hasattr(module, 'run_tsp'):
            return n, None, 0.0, f"Module {program_path} missing 'run_tsp' function"
            
        tour = module.run_tsp(cities)
        
        is_valid, msg = validate_tour(n, tour)
        if not is_valid:
            return n, None, 0.0, msg
            
        dist = calculate_distance(cities, tour)
        return n, list(tour), dist, None
    except Exception as e:
        import traceback
        return n, None, 0.0, f"Error: {e}\n{traceback.format_exc()}"

def main():
    parser = argparse.ArgumentParser(description="TSP Evaluator")
    parser.add_argument("--program_path", type=str, default="tsp/initial.py", help="Path to solution")
    parser.add_argument("--results_dir", type=str, default="tsp/results", help="Dir to save results")
    parser.add_argument("--num_processes", type=int, default=12, help="Parallel processes")
    args = parser.parse_args()

    os.makedirs(args.results_dir, exist_ok=True)
    ns = list(range(20, 41)) # 21 runs
    
    print(f"Evaluating {args.program_path} for n=20..40 using {args.num_processes} processes...")
    
    with multiprocessing.Pool(processes=args.num_processes) as pool:
        raw_results = pool.starmap(worker, [(args.program_path, n) for n in ns])

    metrics = {}
    all_valid = True
    total_negative_distance = 0.0
    
    public_results = {}
    
    for n, tour, dist, err in raw_results:
        if err:
            all_valid = False
            print(f"  n={n}: FAILED - {err}")
            public_results[f"n_{n}"] = {"status": "failed", "error": err}
        else:
            print(f"  n={n}: Distance = {dist:.4f}")
            total_negative_distance -= dist
            public_results[f"n_{n}"] = {"status": "success", "distance": dist}

    metrics = {
        "combined_score": total_negative_distance,
        "all_valid": all_valid,
        "results": public_results
    }

    with open(os.path.join(args.results_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    
    with open(os.path.join(args.results_dir, "correct.json"), "w") as f:
        json.dump(all_valid, f)

    print(f"\nEvaluation Finished.")
    print(f"Combined Score: {total_negative_distance:.4f}")
    print(f"All Valid: {all_valid}")

if __name__ == "__main__":
    main()
