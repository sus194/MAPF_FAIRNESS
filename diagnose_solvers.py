"""
Diagnostic script to understand why all bounded and weighted CBS solvers 
are producing the same results.
"""

import pandas as pd
from cbs_fair import FairCBSSolver
from run_experiments import load_instance

def diagnose_instance(instance_file):
    """Diagnose a single instance to see what's happening."""
    print(f"\n{'='*80}")
    print(f"Diagnosing: {instance_file}")
    print('='*80)
    
    my_map, starts, goals = load_instance(instance_file)
    
    # Test different solvers
    solvers = [
        ("CBS_Standard", {'alpha': 1, 'beta': 0, 'bound': None}),
        ("CBS_Weighted_10", {'alpha': 1, 'beta': 10, 'bound': None}),
        ("CBS_Weighted_50", {'alpha': 1, 'beta': 50, 'bound': None}),
        ("CBS_Bounded_2.0", {'alpha': 1, 'beta': 0, 'bound': 2.0}),
        ("CBS_Bounded_1.5", {'alpha': 1, 'beta': 0, 'bound': 1.5}),
        ("CBS_Bounded_1.2", {'alpha': 1, 'beta': 0, 'bound': 1.2}),
    ]
    
    results = []
    
    for name, config in solvers:
        print(f"\n--- Testing {name} ---")
        solver = FairCBSSolver(my_map, starts, goals, 
                              alpha=config['alpha'], 
                              beta=config['beta'], 
                              stretch_bound=config['bound'])
        
        try:
            # Check initial root node
            print("Computing initial root node...")
            root = {'constraints': [], 'paths': []}
            from single_agent_planner import a_star
            from cbs import detect_collisions
            from metrics import compute_metrics
            
            for i in range(solver.num_of_agents):
                path = a_star(solver.my_map, solver.starts[i], solver.goals[i], 
                            solver.heuristics[i], i, root['constraints'])
                root['paths'].append(path)
            
            root['collisions'] = detect_collisions(root['paths'])
            stats = compute_metrics(root['paths'], solver.starts, solver.goals, solver.heuristics)
            
            print(f"  Initial collisions: {len(root['collisions'])}")
            print(f"  Initial SOC: {stats['soc']}")
            print(f"  Initial max_stretch: {stats['max_stretch']:.4f}")
            print(f"  Initial cost (alpha*SOC + beta*stretch): "
                  f"{config['alpha']}*{stats['soc']} + {config['beta']}*{stats['max_stretch']:.4f} = "
                  f"{config['alpha'] * stats['soc'] + config['beta'] * stats['max_stretch']:.4f}")
            
            if config['bound'] is not None:
                if stats['max_stretch'] > config['bound']:
                    print(f"  WARNING: Initial solution violates bound {config['bound']}!")
                else:
                    print(f"  OK: Initial solution satisfies bound {config['bound']}")
            
            # Now run the full solver
            print("Running full solver...")
            paths = solver.find_solution()
            final_stats = compute_metrics(paths, solver.starts, solver.goals, solver.heuristics)
            
            results.append({
                'solver': name,
                'initial_collisions': len(root['collisions']),
                'initial_soc': stats['soc'],
                'initial_max_stretch': stats['max_stretch'],
                'final_soc': final_stats['soc'],
                'final_max_stretch': final_stats['max_stretch'],
                'cpu_time': solver.CPU_time,
                'nodes_generated': solver.num_of_generated,
                'nodes_expanded': solver.num_of_expanded,
            })
            
            print(f"  Final SOC: {final_stats['soc']}")
            print(f"  Final max_stretch: {final_stats['max_stretch']:.4f}")
            print(f"  CPU time: {solver.CPU_time:.6f}s")
            print(f"  Nodes generated: {solver.num_of_generated}")
            print(f"  Nodes expanded: {solver.num_of_expanded}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                'solver': name,
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    
    # Check if all results are the same
    if len(df) > 0 and 'final_soc' in df.columns:
        unique_socs = df['final_soc'].nunique()
        unique_stretches = df['final_max_stretch'].nunique()
        
        print(f"\nUnique SOC values: {unique_socs}")
        print(f"Unique max_stretch values: {unique_stretches}")
        
        if unique_socs == 1 and unique_stretches == 1:
            print("\nWARNING: All solvers produced identical results!")
            if df['initial_collisions'].iloc[0] == 0:
                print("   Reason: Initial solution has no collisions - all solvers return immediately.")
            else:
                print("   Reason: All solvers found the same solution despite different cost functions.")
                print(f"   The solution happens to be perfectly fair (max_stretch={df['final_max_stretch'].iloc[0]:.4f}),")
                print("   so bounded constraints never prune and weighted costs don't affect the outcome.")

if __name__ == "__main__":
    import sys
    import glob
    import os
    
    if len(sys.argv) > 1:
        instance_name = sys.argv[1]
        # Check if it's already a full path or just a filename
        if os.path.exists(instance_name):
            instance_file = instance_name
        elif os.path.exists(os.path.join("instances", instance_name)):
            instance_file = os.path.join("instances", instance_name)
        else:
            print(f"Error: Could not find instance file: {instance_name}")
            sys.exit(1)
    else:
        # Use first bottleneck instance
        instances = glob.glob("instances/bottleneck*.txt")
        if instances:
            instance_file = instances[0]
        else:
            instances = glob.glob("instances/*.txt")
            instance_file = instances[0] if instances else None
    
    if instance_file:
        diagnose_instance(instance_file)
    else:
        print("No instances found!")

