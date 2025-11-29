# MAPF Fairness Project: Unfair vs. Naive vs. Novel

**Project Goal:** Compare three different approaches to Multi-Agent Path Finding (MAPF) to evaluate the "Price of Fairness."

1.  **Unfair Baseline:** Standard CBS (optimizes efficiency, ignores fairness).
2.  **Naive Approach:** Weighted Sum (tries to balance efficiency/fairness using "magic weights").
3.  **Novel Approach:** Bounded Constraint (guarantees fairness using a strict pruning rule).


## 1. How to Run the Experiments

Everything is automated. You do not need to touch the solver logic.

### Step 1: Generate Test Maps
Run this script to create the "Challenging Instances" (Bottleneck maps and Random maps).
```bash
python generate_instances.py
````

  * **Check:** Look inside the `instances/` folder. You should see files like `bottleneck_10x10_1.txt` and `random_8x8_1.txt`.

### Step 2: Run the Solvers

This script runs all 3 algorithms on all maps and saves the data.

```bash
python run_experiments.py
```

  * **Expectation:** This takes a few minutes. It prints "✓" for successes and "✗" for failures/timeouts.
  * **Output:** A file named **`experiment_results.csv`** will be created. **Use this for your graphs.**

-----

## 2\. The Narrative (For the Report)

When writing the "Methodology" section, use these definitions:

### A. The Baseline (Standard CBS)

  * **Logic:** Minimizes Sum of Costs (SOC) only.
  * **Behavior:** Efficient but "Mean." It will force one agent to wait 50 steps just to save another agent 1 step.
  * **Code Name:** `CBS_Standard`

### B. The Naive Approach (Weighted Sum)

  * **Logic:** Minimizes $Cost = SOC + (\beta \times \text{Fairness})$.
  * **The Problem:** We have to guess the weight $\beta$.
      * If $\beta$ is too low (e.g., 10), the solver ignores fairness.
      * If $\beta$ is too high (e.g., 50), the solver behaves erratically or takes inefficient paths.
  * **Code Name:** `CBS_Weighted_XX`

### C. The Novel Approach (Bounded Constraint)

  * **Logic:** We set a strict rule: "No agent waits more than $K \times$ their optimal path."
  * **The Innovation:** We implemented a **Pruning Rule** in the high-level CBS search. If any node violates the fairness bound $K$, we **discard** it immediately.
  * **The Benefit:** We guarantee fairness (e.g., $K=1.5$ means max 50% delay) without guessing magic numbers.
  * **Code Name:** `CBS_Bounded_XX`

-----

## 3\. Data Dictionary (Understanding the CSV)

When you open `experiment_results.csv`, here is what the columns mean:

| Column | Description |
| :--- | :--- |
| `instance` | The map name (e.g., `bottleneck_10x10_1.txt`). "Bottleneck" maps are the hardest for fairness. |
| `solver` | The algorithm used (Standard, Weighted, or Bounded). |
| `naive_weight` | The $\beta$ value used. Only relevant for Naive solvers. |
| `novel_bound` | The $K$ value used. Only relevant for Novel solvers (e.g., 1.5 = max 50% delay). |
| `soc` | **Sum of Costs (Efficiency).** Lower is better. |
| `max_stretch` | **Fairness Score.** 1.0 is perfect. Higher is unfair. |
| `cpu_time` | How long it took to solve. |
| `success` | `True` if a solution was found. |

-----

## 4\. Graphs to Create (Results Section)

### Graph 1: The "Price of Fairness" (Pareto Frontier)

  * **X-Axis:** Fairness (`max_stretch`)
  * **Y-Axis:** Inefficiency (`soc`)
  * **Goal:** Show that as we force Fairness (moving left on X), the Cost (Y) increases.
  * **Plotting:** Filter for one specific map (e.g., Bottleneck 1). Plot points for `CBS_Standard` vs. `CBS_Bounded_2.0`, `1.5`, `1.2`.

### Graph 2: Stability Comparison

  * **X-Axis:** "Pressure" (Weight $\beta$ OR Bound $K$)
  * **Y-Axis:** Fairness Achieved (`max_stretch`)
  * **Goal:**
      * Show that increasing Naive Weight $\beta$ (10 -\> 50) is **unpredictable** (the stretch might not improve much).
      * Show that tightening Novel Bound $K$ (2.0 -\> 1.5) **guarantees** the stretch improves.

### Graph 3: Scalability

  * **X-Axis:** Map Type (Random vs. Bottleneck)
  * **Y-Axis:** `cpu_time`
  * **Goal:** Show that Fairness is "cheap" on Random maps but "expensive" on Bottleneck maps (Bounded solvers might take longer).

-----

## 5\. Technical Implementation Details

  * **Language:** Python 3
  * **Low-Level Solver:** Space-Time A\* (to handle dynamic obstacles).
  * **High-Level Solver:** Conflict-Based Search (CBS).
  * **Novelty:** Modified `cbs_fair.py` to support `stretch_bound` pruning. Specifically, we modified the `push_node` logic to discard high-level nodes that violate the bound.

<!-- end list -->

```
```