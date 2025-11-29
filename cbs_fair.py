import time as timer
from cbs import CBSSolver, detect_collisions, standard_splitting, disjoint_splitting, paths_violate_constraint
from single_agent_planner import a_star
from metrics import compute_metrics

class FairCBSSolver(CBSSolver):
    """
    Multi-Objective CBS with two modes:
    1. Weighted (Naive): Cost = alpha*SOC + beta*Stretch
    2. Bounded (Novel):  Prune any node where MaxStretch > stretch_bound
    """
    def __init__(self, my_map, starts, goals, alpha=1.0, beta=0.0, stretch_bound=None):
        super().__init__(my_map, starts, goals)
        self.alpha = alpha
        self.beta = beta
        self.stretch_bound = stretch_bound 

    def find_solution(self, disjoint=True):
        self.start_time = timer.time()

        # 1. Root Node Setup
        root = {'cost': 0, 'constraints': [], 'paths': [], 'collisions': []}
        for i in range(self.num_of_agents):
            path = a_star(self.my_map, self.starts[i], self.goals[i], self.heuristics[i],
                          i, root['constraints'])
            if path is None: raise BaseException('No solutions')
            root['paths'].append(path)

        root['collisions'] = detect_collisions(root['paths'])
        stats = compute_metrics(root['paths'], self.starts, self.goals, self.heuristics)
        root['soc'] = stats['soc']
        root['max_stretch'] = stats['max_stretch']
        
        # Initial Pruning (Novel Mode)
        if self.stretch_bound is not None and root['max_stretch'] > self.stretch_bound:
             raise BaseException(f"No solution possible within fairness bound {self.stretch_bound}")

        # Cost Calculation
        root['cost'] = (self.alpha * root['soc']) + (self.beta * root['max_stretch'])
        self.push_node(root)

        # 2. High-Level Search
        while self.open_list:
            node = self.pop_node()

            if len(node['collisions']) == 0:
                self.print_results(node)
                return node['paths']

            collision = node['collisions'][0]
            constraints = disjoint_splitting(collision) if disjoint else standard_splitting(collision)

            for c in constraints:
                child = {'constraints': node['constraints'] + [c], 'paths': list(node['paths'])}
                
                # Replan only affected agents
                to_replan = set([c['agent']])
                if c.get('positive', False):
                    to_replan |= set(paths_violate_constraint(node['paths'], c))

                feasible = True
                for ai in to_replan:
                    new_path = a_star(self.my_map, self.starts[ai], self.goals[ai],
                                      self.heuristics[ai], ai, child['constraints'])
                    if new_path is None:
                        feasible = False; break
                    child['paths'][ai] = new_path

                if not feasible: continue

                # --- METRICS & NOVELTY CHECK ---
                stats = compute_metrics(child['paths'], self.starts, self.goals, self.heuristics)
                
                # NOVELTY: Prune if we violate the hard constraint
                if self.stretch_bound is not None:
                    if stats['max_stretch'] > self.stretch_bound:
                        continue 
                # -------------------------------

                child['soc'] = stats['soc']
                child['max_stretch'] = stats['max_stretch']
                child['collisions'] = detect_collisions(child['paths'])
                
                # Update Priority (Weighted sum is used for sorting the open list)
                child['cost'] = (self.alpha * child['soc']) + (self.beta * child['max_stretch'])
                
                self.push_node(child)
        raise BaseException('No solutions')

    def print_results(self, node):
        print(f"\nSolution Found! CPU: {timer.time() - self.start_time:.2f}s")
        print(f"Weighted Cost: {node['cost']:.2f} | SOC: {node['soc']} | MaxStretch: {node['max_stretch']:.4f}")