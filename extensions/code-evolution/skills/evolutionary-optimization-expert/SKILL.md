---
name: evolutionary-optimization-expert
description: Specialized expertise in the principles of robust, sample-efficient code optimization using evolutionary approaches.
---

# Evolutionary Code Optimization Framework Expert (Darwinian Edition)

When this skill is active, you possess deep knowledge of the "Evolutionary Code Optimization" principles for robust, sample-efficient code optimization. This skill outlines the core concepts, data structures, and algorithmic steps required to build or contribute to a code evolution system.

Evolutionary Code Optimization is a technique that applies the principles of biological evolution — namely selection, mutation, and recombination—to software source code. By leveraging Large Language Models (LLMs) as "intelligent mutation operators," we can iteratively improve a program's performance, efficiency, or accuracy without manual intervention.

With this skill, you are the **Evolutionary Optimization Orchestrator**, an expert in autonomous evolutionary code optimization. Your primary objective is to manage the lifecycle of software evolution, balancing aggressive performance gains with structural integrity and long-term maintainability.


# Background on Evolutionary Code Optimization

## 1. High-Level Architecture

The evolution process follows a continuous loop: **Select** → **Mutate** → **Evaluate** → **Learn**. Unlike traditional genetic algorithms that operate on bitstrings or Abstract Syntax Trees (ASTs), code evolution operates directly on source code, using natural language instructions and structured diffs to guide changes.

### 1.0 The Evolution Loop
1.  **Population Management**: Maintaining a diverse set of programs in a structured database.
2.  **Parent Selection**: Choosing the most promising programs to serve as the basis for the next generation.
3.  **Variation (LLM-driven)**: Using an LLM to suggest code changes based on previous performance.
4.  **Evaluation**: Running the code in a sandbox to measure real-world performance (fitness).
5.  **Novelty Assessment**: Ensuring new proposals are meaningfully different from what has been tried before.
6.  **Meta-Learning**: Analyzing groups of results to provide high-level strategic advice to the mutation engine.

### 1.1 Generations and Termination

In evolutionary optimization, time is measured in **Generations**. 

*   **What is a Generation?**: A generation represents one full iteration of the evolution cycle. In a synchronous system, a generation is the period where the entire population is replaced by its offspring. In modern asynchronous systems, a generation refers to the logical "depth" of a program's lineage—Gen 5 code is a mutation of Gen 4, which came from Gen 3, and so on.
*   **Typical Generation Counts**: The number of generations depends on the complexity of the problem and the available compute budget.
    *   **Quick Proof of Concept**: 10–20 generations.
    *   **Substantial Optimization**: 50–200 generations.
    *   **Complex Algorithmic Discovery**: 500+ generations.
*   **When to Stop**: The process typically terminates when one of the following conditions is met:
    1.  **Budget Exhaustion**: The pre-defined number of generations or a specific API cost limit is reached.
    2.  **Target Fitness**: The program achieves a desired performance threshold (e.g., 99% accuracy or a specific execution time).
    3.  **Convergence**: The system fails to find a meaningful improvement for a large number of generations (stagnation).
    4.  **Manual Intervention**: A user reviews the results in a visualization tool and decides the current "Best Program" is sufficient.

### 1.2 The Evaluation Environment

To run a concrete optimization, you are provided with **Evaluation Mechanism** (often called an "Evaluator" or "Fitness Script"). This code is responsible for executing the proposed program and computing one or more relevant metrics.

*   **The Fitness Function**: This is the primary metric the evolution engine tries to maximize. It must be a numerical value that accurately represents the "quality" of the program. For example, in a sorting algorithm, the fitness might be `1 / execution_time`; in a data-science task, it might be the `F1-Score`.
*   **Multi-Metric Optimization & Constraints**: While there is always a primary fitness function, the evaluator can return multiple metrics. These are used to handle **Constraints** (similar to classical optimization theory):
    *   **Hard Constraints**: Measurements that must stay within certain bounds (e.g., "Memory usage must not exceed 512MB" or "Result must be mathematically correct"). If a hard constraint is violated, the program is usually marked as "incorrect" regardless of its fitness.
    *   **Soft Constraints**: Measurements that are tracked but not strictly enforced, often used during the "Meta-Learning" phase to understand trade-offs (e.g., "The code is faster, but it uses 20% more power").

## 2. Population Management

To prevent the search from getting "stuck" in a local optimum (a good but not perfect solution), the system uses several advanced population strategies.

### Island Models
The population is divided into isolated groups called **Islands**. Evolution happens independently on each island. This allows one island to explore a "risky" algorithmic change while another focuses on "safe" optimizations.
- **Migration**: Periodically, the best programs from one island are "migrated" to another to share successful traits.
- **Initialization**: Typically, the process begins by seeding all islands with an initial baseline program.

### The Elite Archive
A separate **Archive** tracks the best-performing programs ever discovered. These "elites" are frequently used as "inspirations" in prompts to show the LLM examples of what has worked in the past.


## 3. Parent Selection Strategies

Choosing which program to mutate is critical. If we only mutate the best program, we lose diversity. If we choose randomly, we waste compute. Common strategies include:

*   **Power Law Selection**: Favors higher-ranked programs but gives a mathematical "long tail" chance for lower-ranked programs to be selected.
*   **Weighted Sigmoid Selection**: Assigns probabilities based on a combination of fitness score and a "novelty bonus" (favoring programs that haven't produced many children yet).
*   **Beam Search**: Locks onto a specific lineage for several steps to see if a deep chain of mutations leads to a breakthrough.


## 4. Variation Operators (aka Mutations)

The "mutation" is performed by an LLM. The system provides the LLM with the parent code and its performance metrics, then asks for an improvement.

### Mutation Types
1.  **Targeted Diffs (Search/Replace)**: The LLM provides `SEARCH/REPLACE` blocks. This is highly efficient for small, surgical optimizations like reordering loops or changing data structures.
2.  **Full Rewrite**: The LLM rewrites entire logical blocks (marked by delimiters like `EVOLVE-BLOCK-START`). This is useful for fundamental algorithmic shifts.
3.  **Crossover**: The LLM is given *two* different successful programs and asked to merge their best features into a single new implementation.

### Constraint Enforcement
To ensure the LLM doesn't break the entire application, code is wrapped in "evolvable blocks." The evolution engine only allows the LLM to modify code within these markers, keeping the boilerplate, I/O, and evaluation logic immutable. NEVER CHANGE THE CODE OF THE EVALUATOR.

## 5. Diversity and Novelty

A common failure in code evolution is "stagnation," where the LLM suggests the same change (e.g., adding a specific cache) over and over.

### Semantic Novelty Filtering
Before evaluating a program (which is expensive), the system checks if the code is novel:
1.  **Code Embeddings**: The source code is converted into a high-dimensional vector (embedding).
2.  **Cosine Similarity**: If the new code's vector is too close to an existing program in the database, it is rejected as "too similar."
3.  **LLM Novelty Judge**: If the similarity is borderline, a second LLM can be used to judge if the algorithmic approach is meaningfully different, ignoring trivial changes like variable renaming.

## 6. Evaluation and Fitness

Every mutated program is sent to an **Evaluator**. 
*   **Sandbox Execution**: The code is run in a controlled environment.
*   **Metrics Collection**: The system captures scores (e.g., accuracy, throughput), execution time, and error logs.
*   **Validation**: Programs that crash or produce incorrect results are marked as "incorrect" and assigned a fitness of zero, though their code is still stored for the "Meta-Learning" phase to help the system learn what *not* to do.


## 7. Meta-Learning: The Feedback Loop

A unique aspect of modern code evolution is the **Meta-Summarizer**. Every few generations, the system performs a three-step analysis:

1.  **Individual Summarization**: An LLM summarizes the technical changes and results of every program tried recently.
2.  **Global Insight Generation**: An LLM looks at all summaries and identifies patterns (e.g., "Using bit-shifting improved speed by 20%, while recursive approaches consistently timed out").
3.  **Actionable Recommendations**: The LLM generates a list of strategic tips (e.g., "Focus on reducing memory allocations in the inner loop"). These tips are then injected into the prompts for future mutations.


## 8. Dynamic Resource Allocation (Multi-Armed Bandits)

In a large-scale evolution run, not all LLMs are created equal. Some models might be excellent at creative algorithmic design but expensive, while others are fast and cheap for small diffs. 

The system treats LLM selection as a **Multi-Armed Bandit (MAB)** problem, specifically using the **Asymmetric UCB (Upper Confidence Bound)** algorithm:
*   **Arms**: Each available LLM (e.g., GPT-4, Claude 3.5, Gemini 1.5) is an "arm" of the bandit.
*   **Reward**: When a model produces a mutation that improves the fitness score, it receives a "reward."
*   **Exploration vs. Exploitation**: The system balances trying new or underperforming models (exploration) with doubling down on models that are currently providing the best results (exploitation).
*   **Asymmetric Scaling**: The algorithm is tuned to reward "breakthroughs" (large score jumps) more heavily than incremental gains, ensuring the budget shifts toward the most "intelligent" models when the task gets difficult.


## 9. Prompt Engineering for Evolution

The success of a mutation depends on the quality of the prompt sent to the LLM. The **Sampler** dynamically constructs these prompts using four distinct components:

1.  **System Persona**: Sets the stage (e.g., "You are an expert performance engineer specializing in CUDA kernels").
2.  **Evaluation History**: The prompt includes 2–5 previous programs from the **Archive** or the current **Island**. This allows the LLM to perform "In-Context Learning," seeing exactly which code patterns failed and which succeeded.
3.  **Performance Metrics**: Precise numerical feedback (e.g., "This version achieved 450 GFLOPS but had a memory coalescing error").
4.  **Meta-Recommendations**: Actionable strategic tips generated by the **Meta-Summarizer** (e.g., "Previous attempts show that unrolling the loop by a factor of 4 is effective").


## 10. Asynchronous Execution and Scalability

Code evolution is compute-intensive. To handle hundreds of evaluations efficiently, the system uses an **Asynchronous Job Scheduler**:

*   **Non-Blocking Loop**: The main evolution runner doesn't wait for a program to finish evaluating before submitting the next mutation. It maintains a **Job Queue** that keeps the CPU/GPU/LLM resources fully saturated.
*   **Execution Backends**:
    *   **Local**: Jobs run as subprocesses on the current machine.
    *   **Cluster (Slurm/Docker)**: Jobs are dispatched to a high-performance computing cluster, allowing for massive parallelization of evaluations.
*   **Timeout Handling**: Since mutated code can often contain infinite loops or deadlocks, every evaluation is wrapped in a strict "Watchdog" timer that kills stalling processes.


## 11. The Phylogeny of Code

Every program in the database is part of a **Lineage**. By tracking `parent_id` relationships, the system constructs a "Phylogenetic Tree" of the code's evolution.

*   **Lineage Tracking**: We can trace the "Best Program" back through every single mutation to the initial baseline. This reveals the "Evolutionary Path" and the specific insights that led to the final result.
*   **Visual Analysis**: Using the built-in **WebUI**, users can explore this tree, compare diffs between generations, and visualize performance "heatmaps" over time.
*   **Ancestral Analysis**: If a specific mutation (e.g., "Add Caching") consistently leads to high-performing descendants across multiple islands, the Meta-Learner identifies this as a "winning trait."

---

## 🏛 Foundational Themes

### 1. Empirical Rigor & Traceability
Every change must be validated. No optimization is "correct" until it has been evaluated by the project's benchmarking suite and its `combined_score` recorded in the `ProgramDatabase`. Every program must maintain clear **Phylogeny**—we trace the "Best Program" through every mutation back to the initial baseline to understand the specific insights that led to the result.

### 2. Strategic Diversification
Avoid "Hill Climbing" on a single local optimum. You must actively manage multiple **Islands** of evolution, ensuring that architectural diversity is maintained until migration events unify the best traits.

### 3. Sample Efficiency & Meta-Learning
LLM calls and evaluations are your most precious resources. Use the **NoveltyJudge** to prune redundant candidates and the **MetaSummarizer** to turn every evaluation into a lesson for future generations. Prioritize "Big Brain" jumps in strategy over thousands of micro-mutations.

## 📜 Global Mandates

- **Lineage Metadata:** Every new program must have clear lineage metadata (Parent ID, Patch Type, Meta-Recommendations applied).
- **Environment Isolation:** Evaluations must be performed in clean, isolated environments (results directories) to prevent cross-contamination of metrics and ensure safety via sandbox execution.
- **Budget Awareness:** Optimization typically terminates upon **Budget Exhaustion** (API cost or generation limits), **Target Fitness** achievement, or **Convergence** (stagnation).
- **Standardized Reporting:** Use the established formatting for metadata tables and progress logs to ensure the WebUI and CLI tools can parse results accurately.

## 🏛 The How-To of Evolutionary Optimization

### 1. Population Management & Selection
- **Island Models**: Divide the population into isolated groups to explore separate regions of the search space (e.g., "Topological ring shifts" vs. "Numerical refinement"). Periodically **Migrate** elites between islands.
- **Selection Strategies**:
    - **Sigmoid/Power Law Selection**: Favor higher-ranked programs while maintaining a "long tail" chance for lower-ranked programs to prevent stagnation.
    - **Novelty Bonus**: Penalize "Over-sampled Parents" that have produced many children without improvement.
    - **Beam Search**: Lock onto a specific lineage for several steps to see if a deep chain of mutations leads to a breakthrough.
- **Elite Archive**: Maintain a separate archive of the best-performing programs ever discovered to serve as "inspirations" in future prompts.

### 2. The Informed Mutator (Darwinian Optimization)
- **Mutation Types**: 
    - **Targeted Diffs**: Surgical `SEARCH/REPLACE` blocks for small optimizations.
    - **Full Rewrite**: Fundamental algorithmic shifts within protected `# EVOLVE-BLOCK` markers.
    - **Crossover**: Merging features from two different successful programs.
- **Contextual Prompting**: The **Sampler** constructs prompts using the System Persona, Evaluation History (In-Context Learning), Performance Metrics, and Meta-Recommendations.
- **Semantic Novelty Filtering**: Before evaluation, use **Code Embeddings** and **Cosine Similarity** to reject proposals that are too similar to previously tried programs.

### 3. The MetaSummarizer (Strategic Synthesis)
- **Differential Insights**: Focus on *why* a specific code change moved the score. 
- **Global Strategy**: Maintain a running list of "What works" (e.g., "Bit-shifting is 20% faster than division") to guide future generations.
- **Actionable Recommendations**: Generate directives that specify both the *target* and the *tactic* for the next mutation.

### 4. Advanced Orchestration & Scalability
- **Dynamic Resource Allocation (MAB)**: Treat LLM selection as a **Multi-Armed Bandit** problem using the **Asymmetric UCB** algorithm. Reward "breakthroughs" to shift budget toward the most effective models.
- **Asynchronous Execution**: Utilize a non-blocking **Job Scheduler** and **Execution Backends** (Local/Cluster) to keep resources fully saturated.
- **Watchdog Timers**: Every evaluation is wrapped in a strict timer to prevent infinite loops or deadlocks in mutated code.

## 🛠 Specialized Workflows

### The Informed Fix-Cycle
1.  **Extract Failures**: Identify the exact indices of overlapping circles or boundary violations from `stderr_log`.
2.  **Batch Prompting**: Tell the LLM: "Fix overlaps for circles [4, 12, 18] while preserving the layout of Island 2."
3.  **Verification**: Confirm the logic change explicitly addresses the identified failures before full scoring.

### Crossover & Migration
- Periodically synthesize top performers from different islands. 
- **Learning Transfer**: Explain *why* Island A's topological layout should be combined with Island B's numerical solver.

## 📋 Summary Checklist for Optimization Runs
- **Database**: Ensure to keep track of all offsprings and results generated during a run.
- **Islands**: Define logical sub-populations to ensure diversity.
- **Evolve Blocks**: Verify that `# EVOLVE-BLOCK-START` markers protect immutable boilerplate.
- **Evaluator**: Provide a custom script that returns numerical fitness and validates constraints.
