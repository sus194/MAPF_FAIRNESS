# MAPF Fairness Project: Guide

**Project Goal:** We are comparing an **Unfair** approach (Standard CBS) to a **Naive** approach to fairness (Weighted Sum) and a **Novel** approach (Bounded Constraint) in Multi-Agent Path Finding.

### 1\. How to Run the Experiments

Everything is automated. You don't need to touch the solver logic (`cbs_fair.py`).

1.  **Generate the Test Maps:**
    Run this script to create the "Challenging Instances" (Bottleneck maps and Random maps).

    ```bash
    python generate_instances.py
    ```

      * *Check:* Look inside the `instances/` folder. You should see files like `bottleneck_10x10_1.txt` and `random_8x8_1.txt`.

2.  **Run the Main Experiment:**
    This script runs 3 algorithms (Baseline, Weighted, Bounded) on all maps and saves the data.

    ```bash
    python run_experiments.py
    ```

      * *Expectation:* This might take a few minutes. It will print "✓" for successes and "✗" for failures/timeouts.
      * *Output:* A file named **`experiment_results.csv`** will appear. **This is your gold mine for the report.**

-----

### 2\. The Narrative (For the Introduction/Methodology)

When writing the report, you need to explain *why* we built two versions.

  * **The Baseline (Standard CBS):** Optimizes only Sum of Costs (SOC). It is efficient but "mean." It will happily make one agent wait 100 steps to save another agent 1 step.
  * **Approach 1: Naive Weighted Sum (The Strawman):**
      * *Formula:* $Cost = SOC + (\beta \times \text{Fairness})$
      * *The Problem:* We have to guess $\beta$. If we pick $\beta=10$, it does nothing. If $\beta=100$, it might destroy efficiency. It's unpredictable.
  * **Approach 2: Bounded Constraint (Our Novelty):**
      * *Logic:* We don't use weights. We set a strict rule: "No agent waits more than $K$ times their optimal path."
      * *The Benefit:* We can guarantee fairness (e.g., $K=1.5$ means max 50% delay) without guessing magic numbers. We prune the search tree whenever this rule is violated.

-----

### 3\. Graphs You Should Create (For the Results Section)

Use the data in `experiment_results.csv` to plot these three specific charts. These are standard for MAPF papers.

#### **Graph 1: The "Price of Fairness" (Pareto Frontier)**

  * **X-Axis:** Fairness (Max Stretch)
  * **Y-Axis:** Efficiency (Sum of Costs)
  * **What to plot:**
      * Filter for one specific map (e.g., `bottleneck_10x10_1.txt`).
      * Plot a point for **Standard CBS** (High Fairness value, Low Cost).
      * Plot points for **Bounded CBS** with $K=2.0, 1.5, 1.2$.
  * **The Story:** You should see a curve. As we force Fairness (moving left on X), the Cost (Y) will go up. This slope tells us how "expensive" fairness is on that map.

#### **Graph 2: Stability Comparison (Naive vs. Novel)**

  * **X-Axis:** The Fairness "Pressure" (Naive Weight $\beta$ vs. Novel Bound $K$).
  * **Y-Axis:** Max Stretch (Actual Fairness Achieved).
  * **What to plot:**
      * Show that increasing the Naive Weight $\beta$ (e.g., 10 $\to$ 50) **doesn't always** lower the Stretch smoothly (it's erratic).
      * Show that tightening the Novel Bound $K$ (e.g., 2.0 $\to$ 1.5) **guarantees** the drop in Stretch.

#### **Graph 3: Success Rate (Scalability)**

  * **X-Axis:** Map Type (Random vs. Bottleneck).
  * **Y-Axis:** CPU Time (or Success Rate).
  * **The Story:** "Fairness is cheap on Random maps, but expensive on Bottleneck maps."
      * On Random maps, the lines will be close together.
      * On Bottleneck maps, the **Bounded (K=1.2)** solver might timeout or take much longer because it's hard to find a solution where *everyone* gets through the narrow door quickly.

-----

### 4\. Implementation Details (For the Report)

You will need to mention these technical details in the "Implementation" section:

  * **Language:** Python 3.
  * **Low-Level Solver:** Space-Time A\* (to handle dynamic obstacles).
  * **High-Level Solver:** Conflict-Based Search (CBS).
  * **Pruning Rule (The Novelty):** Specifically mention that we modified the `push_node` logic to **discard** any high-level node where $Stretch > Bound$. This effectively prunes the search space of "unfair" solutions.

### 5\. Quick Modifiers

If you need more data points for the graphs, open `run_experiments.py` and modify the `experiments` list:

```python
experiments = [
    # Add more bounds to get a smoother curve
    ("CBS_Bounded_1.8", {'alpha': 1, 'beta': 0, 'bound': 1.8}),
    ("CBS_Bounded_1.1", {'alpha': 1, 'beta': 0, 'bound': 1.1}), 
]
```