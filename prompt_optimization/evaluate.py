"""
Evaluator for Prompt Optimization Challenge
"""

import os
import argparse
import json
import importlib.util
import sys
from typing import Tuple, List, Dict, Any

import time

def clean_json_output(raw_output: str) -> str:
    """
    Strips markdown code blocks and leading/trailing whitespace.
    """
    s = raw_output.strip()
    if s.startswith("```"):
        # Remove starting ```json or ```
        if s.startswith("```json"):
            s = s[7:]
        else:
            s = s[3:]
        # Remove ending ```
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()

def run_extraction_eval(
    program_path: str,
    input_file: str,
    ground_truth_file: str,
) -> Tuple[Dict[str, Any], bool, str]:
    """
    Runs the prompt-based extraction evaluation.
    """
    try:
        # Load the module
        spec = importlib.util.spec_from_file_location("solution", program_path)
        if spec is None or spec.loader is None:
            return {}, False, f"Could not load module from {program_path}"
        module = importlib.util.module_from_spec(spec)
        sys.modules["solution"] = module
        spec.loader.exec_module(module)
        
        if not hasattr(module, "extract_data"):
            return {}, False, "Solution module must have an 'extract_data' function."

        # Read input and ground truth
        with open(input_file, "r") as f:
            inputs = [line.strip() for line in f if line.strip()]
        
        with open(ground_truth_file, "r") as f:
            ground_truth = [json.loads(line) for line in f if line.strip()]

        if len(inputs) != len(ground_truth):
            return {}, False, f"Input size ({len(inputs)}) != Ground truth size ({len(ground_truth)})"

        total_score = 0.0
        details = []
        formatting_failures = 0
        correct_answers = 0

        for i, (text, expected) in enumerate(zip(inputs, ground_truth)):
            try:
                # Call the solution's extraction function
                raw_output = module.extract_data(text)
                
                # Clean and parse JSON
                cleaned_output = clean_json_output(raw_output)
                try:
                    actual = json.loads(cleaned_output)
                    
                    # Check if it matches expected
                    is_correct = True
                    for key in expected:
                        val = actual.get(key)
                        # Handle case where Cost might be returned as a string with $
                        if key == "Cost" and isinstance(val, str):
                            try:
                                val = float(val.replace("$", "").replace(",", ""))
                            except:
                                pass
                        
                        if val != expected[key]:
                            is_correct = False
                            break
                    
                    if is_correct:
                        total_score += 1.0
                        correct_answers += 1
                    else:
                        # Parsed but wrong values
                        pass
                        
                except json.JSONDecodeError:
                    # Formatting failure
                    total_score -= 0.5
                    formatting_failures += 1
                    actual = {"error": "JSONDecodeError", "raw_output": raw_output}
                
                # Sleep to avoid rate limit
                time.sleep(2.1)
            
            except Exception as e:
                return {}, False, f"Error during extraction on item {i}: {e}"

        # Ensure score is not negative for display (optional, but usually scores are >= 0)
        # total_score = max(0.0, total_score)
        
        # Max possible score is len(inputs)
        percentage_score = (total_score / len(inputs)) * 100 if inputs else 0

        metrics = {
            "combined_score": percentage_score,
            "raw_total_score": total_score,
            "correct_answers": correct_answers,
            "formatting_failures": formatting_failures,
            "total_items": len(inputs)
        }
        
        return metrics, True, ""

    except Exception as e:
        import traceback
        return {}, False, f"Error during evaluation: {e}\n{traceback.format_exc()}"

def main(program_path: str, results_dir: str):
    print(f"Evaluating program: {program_path}")
    os.makedirs(results_dir, exist_ok=True)

    input_file = os.path.join(os.path.dirname(__file__), "input.txt")
    ground_truth_file = os.path.join(os.path.dirname(__file__), "ground_truth.jsonl")

    metrics, correct, error_msg = run_extraction_eval(
        program_path=program_path,
        input_file=input_file,
        ground_truth_file=ground_truth_file
    )

    if correct:
        print("Evaluation completed successfully.")
    else:
        print(f"Evaluation failed: {error_msg}")
        metrics = {"combined_score": 0.0, "error": error_msg}

    # Save results
    with open(os.path.join(results_dir, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
    
    with open(os.path.join(results_dir, "correct.json"), "w") as f:
        json.dump(correct, f)

    print("Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prompt Optimization Evaluator")
    parser.add_argument("--program_path", type=str, default="initial.py")
    parser.add_argument("--results_dir", type=str, default="results")
    args = parser.parse_args()
    
    # Resolve paths relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    program_path = os.path.join(script_dir, args.program_path)
    results_dir = os.path.join(script_dir, args.results_dir)
    
    main(program_path, results_dir)
