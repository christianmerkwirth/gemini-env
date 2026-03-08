# 2048 Puzzle Game: Optimization Challenge

2048 is a minimalist, single-player sliding block puzzle game. The objective is to strategically manipulate a grid of numbered tiles to combine them and reach the 2048 tile. In this challenge, you must implement an efficient move selection strategy to maximize the game score while minimizing the number of actions.

## 🛠 Technical Specifications

### Grid Representation
- **Structure**: A **4x4 grid** represented as a `numpy.ndarray` of shape `(4, 4)`.
- **Encoding**: Tiles are stored as **powers of 2**.
    - `0`: Empty cell
    - `1`: $2^1 = 2$
    - `2`: $2^2 = 4$
    - `3`: $2^3 = 8$
    - ...
    - `11`: $2^{11} = 2048$

### Implementation Interface
Your optimization target is the `get_best_move(board: np.ndarray)` function.
- **Input**: Current 4x4 board (power-of-2 encoding).
- **Output**: An `Action` enum value: `Action.UP`, `Action.DOWN`, `Action.LEFT`, or `Action.RIGHT`.
- **Constraint**: Each call to `get_best_move` has a strict **0.11-second time limit**. Exceeding this limit results in a random fallback move and potential evaluation failure.

## 🧬 Scoring and Evaluation

The performance of your implementation is measured by the `combined_score`, which rewards reaching high-value tiles and penalizes excessive moves.

### Scoring Formula
$$combined\_score = \frac{max\_val\_reached}{512} - (num\_actions \times 0.002)$$

### Strategic Implications
- **Primary Goal**: Reach tiles of value **512** or higher. Reaching 512 provides a base score of `1.0`.
- **Efficiency Penalty**: Every move made costs `0.002` points. To achieve a high positive score, you must reach high tiles in as few moves as possible (e.g., reaching 512 in fewer than 500 moves).
- **Termination**: The evaluation episode ends when:
    1. The **2048** tile is reached (Max reward).
    2. No valid moves remain (Game Over).
    3. The maximum allowed steps are reached.
    4. A move selection times out.

## 🎮 Gameplay Mechanics

### Movement and Merging
- **Sliding**: All tiles slide as far as possible in the chosen direction until they hit the edge or another tile.
- **Merging**: Two tiles of the same value collide and merge into their sum ($2^n + 2^n = 2^{n+1}$).
- **Single Merge**: A tile can only merge once per move.
- **New Tiles**: After a move that changes the board, a new tile (90% chance of `1`, 10% chance of `2`) appears in a random empty spot.

## 🎯 Optimization Objectives
1. **Survival**: Avoid filling the board prematurely.
2. **Clustering**: Keep high-value tiles close together (usually in a corner) to facilitate merging.
3. **Efficiency**: Reach the target tile using the most direct path possible to minimize the step penalty.
4. **Speed**: Ensure your heuristic or search algorithm (e.g., Expectimax, Monte Carlo Tree Search) consistently stays within the 110ms execution window.
