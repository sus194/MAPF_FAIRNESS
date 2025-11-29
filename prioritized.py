import time as timer
from single_agent_planner import compute_heuristics, a_star, get_sum_of_cost


class PrioritizedPlanningSolver(object):
    """A planner that plans for each robot sequentially."""

    def __init__(self, my_map, starts, goals):
        """my_map   - list of lists specifying obstacle positions
        starts      - [(x1, y1), (x2, y2), ...] list of start locations
        goals       - [(x1, y1), (x2, y2), ...] list of goal locations
        """

        self.my_map = my_map
        self.starts = starts
        self.goals = goals
        self.num_of_agents = len(goals)

        self.CPU_time = 0

        # compute heuristics for the low-level search
        self.heuristics = []
        for goal in self.goals:
            self.heuristics.append(compute_heuristics(my_map, goal))

    def find_solution(self):
        """ Finds paths for all agents from their start locations to their goal locations."""
        start_time = timer.time()
        result = []
        constraints = []

        rows = len(self.my_map)
        cols = len(self.my_map[0])
        GRID_AREA = rows * cols

        # Optional: a conservative upper bound for later agents.
        # We’ll grow this as we add higher-priority paths.
        accumulated_len = 0

        for i in range(self.num_of_agents):  # plan in priority order
            # ---- 2.4 time horizon for agent i ----
            # lower bound: Manhattan dist (use heuristic at start if available)
            h_lb = self.heuristics[i].get(self.starts[i], 0)
            # upper bound: previous paths + grid area buffer
            max_timestep = accumulated_len + GRID_AREA + h_lb

            # Call low-level A* (with optional horizon if you added it; see a_star patch below)
            try:
                path = a_star(self.my_map, self.starts[i], self.goals[i],
                            self.heuristics[i], i, constraints, max_timestep=max_timestep)
            except TypeError:
                # If you didn’t patch a_star for horizon, call without it
                path = a_star(self.my_map, self.starts[i], self.goals[i],
                            self.heuristics[i], i, constraints)

            if path is None:
                raise BaseException('No solutions')
            result.append(path)
            accumulated_len += (len(path) - 1)

            # ----------------------------
            # Task 2.1: Vertex constraints
            # ----------------------------
            for t, loc in enumerate(path):
                for j in range(i + 1, self.num_of_agents):
                    constraints.append({'agent': j, 'loc': [loc], 'timestep': t})

            # --------------------------
            # Task 2.2: Edge constraints
            # --------------------------
            for t in range(len(path) - 1):
                curr = path[t]
                nxt = path[t + 1]
                for j in range(i + 1, self.num_of_agents):
                    # forbid j from doing the opposite move at arrival time t+1
                    constraints.append({'agent': j, 'loc': [nxt, curr], 'timestep': t + 1})

            # --------------------------------
            # Task 2.3: Goal-holding constraints
            # --------------------------------
            goal = path[-1]
            Tg = len(path) - 1
            # Hold the goal "forever" = for a finite horizon window.
            # Use a window large enough so any later agent can't step onto i's goal.
            hold_until = accumulated_len + GRID_AREA  # generous horizon
            for t in range(Tg, hold_until + 1):
                for j in range(i + 1, self.num_of_agents):
                    constraints.append({'agent': j, 'loc': [goal], 'timestep': t})

        self.CPU_time = timer.time() - start_time

        print("\n Found a solution! \n")
        print("CPU time (s):    {:.2f}".format(self.CPU_time))
        print("Sum of costs:    {}".format(get_sum_of_cost(result)))
        return result

