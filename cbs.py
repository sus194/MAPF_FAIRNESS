import time as timer
import heapq
import random
from single_agent_planner import compute_heuristics, a_star, get_location, get_sum_of_cost


def detect_collision(path1, path2):
    """
    Return the first collision dict between two paths, or None.
    Collision format:
      Vertex: {'loc': [(x,y)], 'timestep': t}
      Edge:   {'loc': [(x1,y1),(x2,y2)], 'timestep': t}  # arrival time t (move from t-1 -> t)
    """
    T = max(len(path1), len(path2))  # search until both would be waiting at goals
    for t in range(T):
        l1 = get_location(path1, t)
        l2 = get_location(path2, t)
        # Vertex collision
        if l1 == l2:
            return {'loc': [l1], 'timestep': t}
        # Edge collision (swap) at arrival time t
        if t > 0:
            l1_prev = get_location(path1, t - 1)
            l2_prev = get_location(path2, t - 1)
            if l1_prev == l2 and l2_prev == l1:
                return {'loc': [l1_prev, l1], 'timestep': t}
    return None


def detect_collisions(paths):
    """
    Return list of first collisions between all robot pairs.
    Each item has keys: 'a1', 'a2', 'loc', 'timestep'.
    """
    collisions = []
    n = len(paths)
    for i in range(n):
        for j in range(i + 1, n):
            c = detect_collision(paths[i], paths[j])
            if c is not None:
                c['a1'] = i
                c['a2'] = j
                collisions.append(c)
    return collisions


def standard_splitting(collision):
    """
    From a collision, return two negative constraints to resolve it.
    Vertex: forbid each agent at that vertex at that timestep.
    Edge:   forbid each agent to traverse the conflicting edge at that timestep.
    """
    a1, a2 = collision['a1'], collision['a2']
    t = collision['timestep']
    loc = collision['loc']
    if len(loc) == 1:  # vertex
        v = loc[0]
        return [
            {'agent': a1, 'loc': [v], 'timestep': t},
            {'agent': a2, 'loc': [v], 'timestep': t},
        ]
    else:  # edge
        u, v = loc[0], loc[1]  # a1: u->v, a2: v->u
        return [
            {'agent': a1, 'loc': [u, v], 'timestep': t},
            {'agent': a2, 'loc': [v, u], 'timestep': t},
        ]


def disjoint_splitting(collision):
    ##############################
    # Task 4.1: Return a list of (two) constraints to resolve the given collision
    #           Vertex collision: the first constraint enforces one agent to be at the specified location at the
    #                            specified timestep, and the second constraint prevents the same agent to be at the
    #                            same location at the timestep.
    #           Edge collision: the first constraint enforces one agent to traverse the specified edge at the
    #                          specified timestep, and the second constraint prevents the same agent to traverse the
    #                          specified edge at the specified timestep
    #           Choose the agent randomly
    a1, a2 = collision['a1'], collision['a2']
    t = collision['timestep']
    loc = collision['loc']  # [(x,y)] or [(x1,y1),(x2,y2)]
    chosen = random.choice([a1, a2])
    return [
        {'agent': chosen, 'loc': loc, 'timestep': t, 'positive': True},
        {'agent': chosen, 'loc': loc, 'timestep': t, 'positive': False},
    ]

def paths_violate_constraint(paths, constraint):
    violators = []
    t = constraint['timestep']
    loc = constraint['loc']
    is_pos = constraint.get('positive', False)
    assert is_pos

    for i, p in enumerate(paths):
        # skip the agent that the positive constraint is for
        if i == constraint['agent']:
            continue
        if len(loc) == 1:
            if get_location(p, t) == tuple(loc[0]):
                violators.append(i)
        else:
            if get_location(p, t-1) == tuple(loc[0]) and get_location(p, t) == tuple(loc[1]):
                violators.append(i)
    return violators


class CBSSolver(object):
    """The high-level search of CBS."""

    def __init__(self, my_map, starts, goals):
        """my_map   - list of lists specifying obstacle positions
        starts      - [(x1, y1), (x2, y2), ...] list of start locations
        goals       - [(x1, y1), (x2, y2), ...] list of goal locations
        """

        self.my_map = my_map
        self.starts = starts
        self.goals = goals
        self.num_of_agents = len(goals)

        self.num_of_generated = 0
        self.num_of_expanded = 0
        self.CPU_time = 0

        self.open_list = []

        # compute heuristics for the low-level search
        self.heuristics = []
        for goal in self.goals:
            self.heuristics.append(compute_heuristics(my_map, goal))

    def push_node(self, node):
        heapq.heappush(self.open_list, (node['cost'], len(node['collisions']), self.num_of_generated, node))
        print("Generate node {}".format(self.num_of_generated))
        self.num_of_generated += 1

    def pop_node(self):
        _, _, id, node = heapq.heappop(self.open_list)
        print("Expand node {}".format(id))
        self.num_of_expanded += 1
        return node

    def find_solution(self, disjoint=True):
        """ Finds paths for all agents from their start locations to their goal locations

        disjoint    - use disjoint splitting or not
        """

        self.start_time = timer.time()

        # Generate the root node
        # constraints   - list of constraints
        # paths         - list of paths, one for each agent
        #               [[(x11, y11), (x12, y12), ...], [(x21, y21), (x22, y22), ...], ...]
        # collisions     - list of collisions in paths
        root = {'cost': 0,
                'constraints': [],
                'paths': [],
                'collisions': []}
        for i in range(self.num_of_agents):  # Find initial path for each agent
            path = a_star(self.my_map, self.starts[i], self.goals[i], self.heuristics[i],
                          i, root['constraints'])
            if path is None:
                raise BaseException('No solutions')
            root['paths'].append(path)

        root['cost'] = get_sum_of_cost(root['paths'])
        root['collisions'] = detect_collisions(root['paths'])
        self.push_node(root)

        # Task 3.1: Testing
        print(root['collisions'])

        # Task 3.2: Testing
        for collision in root['collisions']:
            print(standard_splitting(collision))

        ##############################
        # Task 3.3: High-Level Search
        #           Repeat the following as long as the open list is not empty:
        #             1. Get the next node from the open list (you can use self.pop_node()
        #             2. If this node has no collision, return solution
        #             3. Otherwise, choose the first collision and convert to a list of constraints (using your
        #                standard_splitting function). Add a new child node to your open list for each constraint
        #           Ensure to create a copy of any objects that your child nodes might inherit
        while self.open_list:
            node = self.pop_node()

            # Goal test
            if len(node['collisions']) == 0:
                self.print_results(node)
                return node['paths']

            # Choose the first collision
            collision = node['collisions'][0]
            constraints_to_apply = disjoint_splitting(collision) if disjoint else standard_splitting(collision)

            for c in constraints_to_apply:
                child = {
                    'constraints': node['constraints'] + [c],
                    'paths': list(node['paths']),
                }

                # which agents must be replanned?
                to_replan = set([c['agent']])
                if c.get('positive', False):
                    to_replan |= set(paths_violate_constraint(node['paths'], c))

                feasible = True
                for ai in to_replan:
                    new_path = a_star(self.my_map, self.starts[ai], self.goals[ai],
                                    self.heuristics[ai], ai, child['constraints'])
                    if new_path is None:
                        feasible = False
                        break
                    child['paths'][ai] = new_path

                if not feasible:
                    continue

                child['cost'] = get_sum_of_cost(child['paths'])
                child['collisions'] = detect_collisions(child['paths'])
                self.push_node(child)
        raise BaseException('No solutions')


    def print_results(self, node):
        print("\n Found a solution! \n")
        CPU_time = timer.time() - self.start_time
        print("CPU time (s):    {:.2f}".format(CPU_time))
        print("Sum of costs:    {}".format(get_sum_of_cost(node['paths'])))
        print("Expanded nodes:  {}".format(self.num_of_expanded))
        print("Generated nodes: {}".format(self.num_of_generated))
