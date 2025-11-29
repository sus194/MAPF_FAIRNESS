import numpy as np

def compute_metrics(paths, starts, goals, heuristics):
    """
    Computes SOC, Makespan, and Fairness (Stretch) metrics.
    """
    num_agents = len(paths)
    costs = []
    stretches = []
    
    for i in range(num_agents):
        # Actual path cost
        actual_cost = len(paths[i]) - 1
        costs.append(actual_cost)
        
        # Optimal cost (Shortest Path if alone)
        # We retrieve the cost of the start_node from the heuristic table
        # Note: Heuristics in your code store cost-to-go from location to goal.
        optimal_cost = heuristics[i].get(starts[i], float('inf'))
        
        # Calculate Stretch (Fairness Metric)
        if optimal_cost == 0:
            stretch = 1.0 if actual_cost == 0 else float('inf')
        else:
            stretch = actual_cost / optimal_cost
        stretches.append(stretch)

    soc = sum(costs)
    makespan = max(costs) if costs else 0
    max_stretch = max(stretches) if stretches else 0
    avg_stretch = np.mean(stretches) if stretches else 0
    
    return {
        "soc": soc,
        "makespan": makespan,
        "max_stretch": max_stretch,
        "avg_stretch": avg_stretch,
        "all_stretches": stretches
    }

def print_metrics(metrics):
    print(f"{'Sum of Costs:':<20} {metrics['soc']}")
    print(f"{'Makespan:':<20} {metrics['makespan']}")
    print(f"{'Max Stretch (Fairness):':<20} {metrics['max_stretch']:.4f}")
    print(f"{'Avg Stretch:':<20} {metrics['avg_stretch']:.4f}")