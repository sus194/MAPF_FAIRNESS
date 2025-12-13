import argparse
import glob
import os
import pandas as pd
import time
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
            line = f.readline().strip().replace(' ', '').replace('\t', '')
            my_map.append([c == '@' for c in line])
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
    alpha = config.get('alpha', 1.0)
    beta = config.get('beta', 0.0)
    bound = config.get('bound', None)

    if solver_name == "Prioritized":
        solver = PrioritizedPlanningSolver(my_map, starts, goals)
    else:
        # 60s is good
        solver = FairCBSSolver(my_map, starts, goals, alpha, beta, bound, time_limit=60)

    try:
        t_start = time.perf_counter()
        paths = solver.find_solution()
        t_end = time.perf_counter()
        cpu_time = t_end - t_start

        stats = compute_metrics(paths, starts, goals, solver.heuristics)
        return {
            "success": True,
            "soc": stats['soc'],
            "max_stretch": stats['max_stretch'],
            "cpu_time": cpu_time
        }
    except BaseException as e:
        return {"success": False, "soc": None, "max_stretch": None, "cpu_time": 60.0}

def main():
    # Run ALL 3
    instance_files = [
        "instances/asymmetric_conflict.txt",
        "instances/random_scalability.txt",
        "instances/airport_mini.txt"
    ]
    results = []

    experiments = [
        ("Prioritized",  {'alpha': 1, 'beta': 0, 'bound': None}),
        ("CBS_Standard", {'alpha': 1, 'beta': 0, 'bound': None}),
        ("CBS_Weighted_50", {'alpha': 1, 'beta': 50, 'bound': None}),
        ("CBS_Bounded_2.0", {'alpha': 1, 'beta': 0, 'bound': 2.0}), 
        ("CBS_Bounded_1.5", {'alpha': 1, 'beta': 0, 'bound': 1.5}), 
        ("CBS_Bounded_1.3", {'alpha': 1, 'beta': 0, 'bound': 1.3}), 
        ("CBS_Bounded_1.2", {'alpha': 1, 'beta': 0, 'bound': 1.2}), 
    ]

    for fname in instance_files:
        if not os.path.exists(fname): continue
        print(f"Processing {os.path.basename(fname)}...")
        for name, config in experiments:
            print(f"  > {name}...", end="", flush=True)
            data = run_single_instance(name, fname, config)
            row = {"instance": os.path.basename(fname), "solver": name, **data}
            results.append(row)
            print(f" {'✓' if data['success'] else '✗'} ({data['cpu_time']:.4f}s)")

    pd.DataFrame(results).to_csv("experiment_results.csv", index=False)
    print("Done. Saved to experiment_results.csv")

if __name__ == "__main__":
    main()