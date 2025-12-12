import argparse
import glob
import os
import pandas as pd
from prioritized import PrioritizedPlanningSolver
from cbs_fair import FairCBSSolver
from metrics import compute_metrics

def load_instance(fname):
    with open(fname, 'r') as f:
        line = f.readline().split()
        if not line: return None, None, None
        rows, cols = int(line[0]), int(line[1])
        
        my_map = []
        for _ in range(rows):
            line = f.readline().strip()
            clean_line = line.replace(' ', '').replace('\t', '')
            row_bools = [char == '@' for char in clean_line]
            my_map.append(row_bools)
            
        num_agents = int(f.readline().strip())
        starts = []
        goals = []
        for _ in range(num_agents):
            line = f.readline().split()
            starts.append((int(line[0]), int(line[1])))
            goals.append((int(line[2]), int(line[3])))
            
    return my_map, starts, goals

def run_single_instance(solver_name, instance_file, config):
    my_map, starts, goals = load_instance(instance_file)
    
    # Unpack config
    alpha = config.get('alpha', 1.0)
    beta = config.get('beta', 0.0)
    bound = config.get('bound', None)

    if solver_name == "Prioritized":
        solver = PrioritizedPlanningSolver(my_map, starts, goals)
    else:
        # Use FairCBS for everything else (Standard, Weighted, Bounded)
        solver = FairCBSSolver(my_map, starts, goals, alpha=alpha, beta=beta, stretch_bound=bound)

    try:
        paths = solver.find_solution()
        stats = compute_metrics(paths, starts, goals, solver.heuristics)
        return {
            "success": True,
            "soc": stats['soc'],
            "makespan": stats['makespan'],
            "max_stretch": stats['max_stretch'],
            "cpu_time": solver.CPU_time if hasattr(solver, 'CPU_time') else 0
        }
    except BaseException as e:
        return {"success": False, "error": str(e)}

def main():
    instance_files = sorted(glob.glob("instances/*.txt"))
    results = []

    print(f"Found {len(instance_files)} instances. Starting experiments...")

    # --- DEFINING THE COMPARISON ---
    experiments = [
        # 1. BASELINE (Unfair)
        ("Prioritized",  {'alpha': 1, 'beta': 0, 'bound': None}),
        ("CBS_Standard", {'alpha': 1, 'beta': 0, 'bound': None}),

        # 2. NAIVE APPROACH (Weighted Sum)
        # We try to 'guess' a weight that makes it fair.
        ("CBS_Weighted_10", {'alpha': 1, 'beta': 10, 'bound': None}),
        ("CBS_Weighted_50", {'alpha': 1, 'beta': 50, 'bound': None}),

        # 3. NOVEL APPROACH (Bounded / Constraint-Based)
        # We explicitly forbid unfair paths > K.
        ("CBS_Bounded_2.0", {'alpha': 1, 'beta': 0, 'bound': 2.0}), # <100% delay
        ("CBS_Bounded_1.5", {'alpha': 1, 'beta': 0, 'bound': 1.5}), # <50% delay
        ("CBS_Bounded_1.2", {'alpha': 1, 'beta': 0, 'bound': 1.2}), # <20% delay
    ]

    for fname in instance_files:
        print(f"\nProcessing {os.path.basename(fname)}...")
        for name, config in experiments:
            print(f"  > {name}...", end="", flush=True)
            
            data = run_single_instance(name, fname, config)
            
            row = {
                "instance": os.path.basename(fname),
                "solver": name,
                "naive_weight": config['beta'],
                "novel_bound": config['bound'],
                **data
            }
            results.append(row)
            success_mark = "[OK]" if data.get('success') else "[FAIL]"
            print(f" {success_mark}")

    df = pd.DataFrame(results)
    df.to_csv("experiment_results.csv", index=False)
    print("\nExperiments Completed. Results saved to 'experiment_results.csv'.")

if __name__ == "__main__":
    main()