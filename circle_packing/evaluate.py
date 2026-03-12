"""
Evaluator for circle packing example (n=26) with improved timeout handling
"""

import os
import argparse
import json
import numpy as np
from typing import Tuple, Optional, List, Dict, Any

import importlib.util
import sys

def run_shinka_eval(
    program_path: str,
    results_dir: str,
    experiment_fn_name: str,
    num_runs: int,
    timeout: int,
    get_experiment_kwargs: Any,
    validate_fn: Any,
    aggregate_metrics_fn: Any,
) -> Tuple[Dict[str, Any], bool, str]:
    """Stub implementation of run_shinka_eval."""
    try:
        spec = importlib.util.spec_from_file_location("module.name", program_path)
        if spec is None or spec.loader is None:
            return {}, False, f"Could not load module from {program_path}"
        module = importlib.util.module_from_spec(spec)
        sys.modules["module.name"] = module
        spec.loader.exec_module(module)
        
        experiment_fn = getattr(module, experiment_fn_name)
        
        results = []
        all_errors = []
        all_valid = True
        
        for i in range(num_runs):
            kwargs = get_experiment_kwargs(i)
            # Note: timeout is not implemented in this simple stub
            res = experiment_fn(**kwargs)
            results.append(res)
            
            # Extract n from kwargs to pass to validate_fn if needed, 
            # though adapted_validate_packing will infer it from the result shape.
            is_valid, msg = validate_fn(res)
            if not is_valid:
                all_valid = False
                all_errors.append(f"Run {i} (n={kwargs.get('n')}): {msg}")
        
        metrics = aggregate_metrics_fn(results)
        error_summary = "\n".join(all_errors) if all_errors else ""
        return metrics, all_valid, error_summary
    except Exception as e:
        import traceback
        return {}, False, f"Error during evaluation: {e}\n{traceback.format_exc()}"


def format_centers_string(centers: np.ndarray) -> str:
    """Formats circle centers into a multi-line string for display."""
    return "\n".join(
        [
            f"  centers[{i}] = ({x_coord:.4f}, {y_coord:.4f})"
            for i, (x_coord, y_coord) in enumerate(centers)
        ]
    )


def adapted_validate_packing(
    run_output: Tuple[np.ndarray, np.ndarray, float],
    atol=1e-6,
) -> Tuple[bool, Optional[str]]:
    """
    Validates circle packing results based on the output of 'run_packing'.

    Args:
        run_output: Tuple (centers, radii, reported_sum) from run_packing.

    Returns:
        (is_valid: bool, error_message: Optional[str])
    """
    centers, radii, reported_sum = run_output
    msg = "The circles are placed correctly. There are no overlaps or any circles outside the unit square."
    if not isinstance(centers, np.ndarray):
        centers = np.array(centers)
    if not isinstance(radii, np.ndarray):
        radii = np.array(radii)

    n_circles = centers.shape[0]
    if radii.shape != (n_circles,):
        msg = f"Radii shape incorrect. Expected ({n_circles},), got {radii.shape}"
        return False, msg

    if np.any(radii < 0):
        negative_indices = np.where(radii < 0)[0]
        msg = f"Negative radii found for circles at indices: {negative_indices}"
        return False, msg

    if not np.isclose(np.sum(radii), reported_sum, atol=atol):
        msg = (
            f"Sum of radii ({np.sum(radii):.6f}) does not match "
            f"reported ({reported_sum:.6f})"
        )
        return False, msg

    for i in range(n_circles):
        x, y = centers[i]
        r = radii[i]
        is_outside = (
            x - r < -atol or x + r > 1 + atol or y - r < -atol or y + r > 1 + atol
        )
        if is_outside:
            msg = (
                f"Circle {i} (x={x:.4f}, y={y:.4f}, r={r:.4f}) is outside unit square."
            )
            return False, msg

    for i in range(n_circles):
        for j in range(i + 1, n_circles):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
            if dist < radii[i] + radii[j] - atol:
                msg = (
                    f"Circles {i} & {j} overlap. Dist: {dist:.4f}, "
                    f"Sum Radii: {(radii[i] + radii[j]):.4f}"
                )
                return False, msg
    return True, msg


def get_circle_packing_kwargs(run_index: int) -> Dict[str, Any]:
    """Provides keyword arguments for circle packing runs (n from 10 to 30)."""
    return {"n": 10 + run_index}


def aggregate_circle_packing_metrics(
    results: List[Tuple[np.ndarray, np.ndarray, float]], results_dir: str
) -> Dict[str, Any]:
    """
    Aggregates metrics for circle packing for multiple runs (n from 10 to 30).
    Saves results for each run in extra.npz.
    """
    if not results:
        return {"combined_score": 0.0, "error": "No results to aggregate"}

    total_sum_of_radii = 0.0
    all_public_metrics = {}
    all_private_metrics = {}

    for i, res in enumerate(results):
        centers, radii, reported_sum = res
        n = centers.shape[0]
        total_sum_of_radii += float(reported_sum)
        
        all_public_metrics[f"n_{n}"] = {
            "num_circles": n,
            "reported_sum": float(reported_sum)
        }
        all_private_metrics[f"n_{n}"] = {
            "centers": centers.tolist(),
            "radii": radii.tolist()
        }

    metrics = {
        "combined_score": total_sum_of_radii,
        "public": all_public_metrics,
        "private": all_private_metrics,
    }

    # Save detailed data for all runs
    extra_file = os.path.join(results_dir, "extra.npz")
    try:
        save_kwargs = {}
        for i, res in enumerate(results):
            centers, radii, reported_sum = res
            n = centers.shape[0]
            save_kwargs[f"centers_{n}"] = centers
            save_kwargs[f"radii_{n}"] = radii
            save_kwargs[f"reported_sum_{n}"] = reported_sum
            
        np.savez(extra_file, **save_kwargs)
        print(f"Detailed packing data for all runs saved to {extra_file}")
    except Exception as e:
        print(f"Error saving extra.npz: {e}")
        metrics["extra_npz_save_error"] = str(e)

    return metrics


def main(program_path: str, results_dir: str, timeout: int = 60):
    """Runs the circle packing evaluation using shinka.eval."""
    print(f"Evaluating program: {program_path}")
    print(f"Saving results to: {results_dir}")
    os.makedirs(results_dir, exist_ok=True)

    num_experiment_runs = 21

    # Define a nested function to pass results_dir to the aggregator
    def _aggregator_with_context(
        r: List[Tuple[np.ndarray, np.ndarray, float]],
    ) -> Dict[str, Any]:
        return aggregate_circle_packing_metrics(r, results_dir)

    metrics, correct, error_msg = run_shinka_eval(
        program_path=program_path,
        results_dir=results_dir,
        experiment_fn_name="run_packing",
        num_runs=num_experiment_runs,
        timeout=timeout,
        get_experiment_kwargs=get_circle_packing_kwargs,
        validate_fn=adapted_validate_packing,
        aggregate_metrics_fn=_aggregator_with_context,
    )

    if correct:
        print("Evaluation and Validation completed successfully.")
    else:
        print(f"Evaluation or Validation failed: {error_msg}")

    metrics_file = os.path.join(results_dir, "metrics.json")
    try:
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=4)
        print(f"Metrics saved to {metrics_file}")
    except Exception as e:
        print(f"Error saving metrics.json: {e}")

    correct_file = os.path.join(results_dir, "correct.json")
    try:
        with open(correct_file, "w") as f:
            json.dump(correct, f)
        print(f"Correctness status saved to {correct_file}")
    except Exception as e:
        print(f"Error saving correct.json: {e}")

    print("Metrics:")
    for key, value in metrics.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: <string_too_long_to_display>")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Circle packing evaluator using shinka.eval"
    )
    parser.add_argument(
        "--program_path",
        type=str,
        default="circle_packing/initial.py",
        help="Path to program to evaluate (must contain 'run_packing')",
    )
    parser.add_argument(
        "--results_dir",
        type=str,
        default="circle_packing/results",
        help="Dir to save results (metrics.json, correct.json, extra.npz)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout for each evaluation run in seconds",
    )
    parsed_args = parser.parse_args()
    main(parsed_args.program_path, parsed_args.results_dir, parsed_args.timeout)
