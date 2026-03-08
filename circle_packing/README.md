# Circle Packing Project

This project implements and evaluates a circle packing algorithm for $n=26$ circles in a unit square.

## Dependencies

- Python 3.12+
- `numpy`
- `scipy`
- `pandas`

Managed with [uv](https://github.com/astral-sh/uv).

## Getting Started

1.  **Install dependencies**:
    ```bash
    uv sync
    ```

2.  **Run the evaluation**:
    ```bash
    uv run python evaluate.py
    ```

    By default, it evaluates `initial.py` and saves to `results/`. You can specify a different program path or results directory:
    ```bash
    uv run python evaluate.py --program_path initial.py --results_dir my_custom_results
    ```

3.  **Outputs**:
    - The evaluation script will print metrics to the console.
    - Detailed data will be saved to the `results/` directory, including `extra.npz`.

## Project Structure

- `evaluate.py`: The main evaluation script (includes a stubbed evaluator).
- `initial.py`: The initial circle packing constructor.
- `viz_circles.ipynb`: A Jupyter notebook for visualizing the packing.
- `pyproject.toml`: Project configuration and dependencies.
