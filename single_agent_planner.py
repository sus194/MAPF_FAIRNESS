import heapq

def move(loc, dir):
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    return loc[0] + directions[dir][0], loc[1] + directions[dir][1]


def get_sum_of_cost(paths):
    rst = 0
    for path in paths:
        rst += len(path) - 1
    return rst


def compute_heuristics(my_map, goal):
    # Use Dijkstra to build a shortest-path tree rooted at the goal location
    open_list = []
    closed_list = dict()
    root = {'loc': goal, 'cost': 0}
    heapq.heappush(open_list, (root['cost'], goal, root))
    closed_list[goal] = root
    while len(open_list) > 0:
        (cost, loc, curr) = heapq.heappop(open_list)
        for dir in range(4):
            child_loc = move(loc, dir)
            child_cost = cost + 1
            if child_loc[0] < 0 or child_loc[0] >= len(my_map) \
               or child_loc[1] < 0 or child_loc[1] >= len(my_map[0]):
               continue
            if my_map[child_loc[0]][child_loc[1]]:
                continue
            child = {'loc': child_loc, 'cost': child_cost}
            if child_loc in closed_list:
                existing_node = closed_list[child_loc]
                if existing_node['cost'] > child_cost:
                    closed_list[child_loc] = child
                    # open_list.delete((existing_node['cost'], existing_node['loc'], existing_node))
                    heapq.heappush(open_list, (child_cost, child_loc, child))
            else:
                closed_list[child_loc] = child
                heapq.heappush(open_list, (child_cost, child_loc, child))

    # build the heuristics table
    h_values = dict()
    for loc, node in closed_list.items():
        h_values[loc] = node['cost']
    return h_values


# def build_constraint_table(constraints, agent):
#     ##############################
#     # Task 1.2/1.3: Return a table that constains the list of constraints of
#     #               the given agent for each time step. The table can be used
#     #               for a more efficient constraint violation check in the 
#     #               is_constrained function.

#     pass


def get_location(path, time):
    if time < 0:
        return path[0]
    elif time < len(path):
        return path[time]
    else:
        return path[-1]  # wait at the goal location


def get_path(goal_node):
    path = []
    curr = goal_node
    while curr is not None:
        path.append(curr['loc'])
        curr = curr['parent']
    path.reverse()
    return path


# def is_constrained(curr_loc, next_loc, next_time, constraint_table):
#     ##############################
#     # Task 1.2/1.3: Check if a move from curr_loc to next_loc at time step next_time violates
#     #               any given constraint. For efficiency the constraints are indexed in a constraint_table
#     #               by time step, see build_constraint_table.

#     pass


def push_node(open_list, node):
    heapq.heappush(open_list, (node['g_val'] + node['h_val'], node['h_val'], node['loc'], node))


def pop_node(open_list):
    _, _, _, curr = heapq.heappop(open_list)
    return curr


def compare_nodes(n1, n2):
    """Return true is n1 is better than n2."""
    return n1['g_val'] + n1['h_val'] < n2['g_val'] + n2['h_val']


# def a_star(my_map, start_loc, goal_loc, h_values, agent, constraints):
#     """ my_map      - binary obstacle map
#         start_loc   - start position
#         goal_loc    - goal position
#         agent       - the agent that is being re-planned
#         constraints - constraints defining where robot should or cannot go at each timestep
#     """

#     ##############################
#     # Task 1.1: Extend the A* search to search in the space-time domain
#     #           rather than space domain, only.

#     open_list = []
#     closed_list = dict()
#     earliest_goal_timestep = 0
#     h_value = h_values[start_loc]
#     root = {'loc': start_loc, 'g_val': 0, 'h_val': h_value, 'parent': None}
#     push_node(open_list, root)
#     closed_list[(root['loc'])] = root
#     while len(open_list) > 0:
#         curr = pop_node(open_list)
#         #############################
#         # Task 1.4: Adjust the goal test condition to handle goal constraints
#         if curr['loc'] == goal_loc:
#             return get_path(curr)
#         for dir in range(4):
#             child_loc = move(curr['loc'], dir)
#             if my_map[child_loc[0]][child_loc[1]]:
#                 continue
#             child = {'loc': child_loc,
#                     'g_val': curr['g_val'] + 1,
#                     'h_val': h_values[child_loc],
#                     'parent': curr}
#             if (child['loc']) in closed_list:
#                 existing_node = closed_list[(child['loc'])]
#                 if compare_nodes(child, existing_node):
#                     closed_list[(child['loc'])] = child
#                     push_node(open_list, child)
#             else:
#                 closed_list[(child['loc'])] = child
#                 push_node(open_list, child)

#     return None  # Failed to find solutions

# --- in single_agent_planner.py ---

def build_constraint_table(constraints, agent):
    """
    Return {
      'neg': {t: [constraint, ...]},   # constraints that forbid this agent's states/moves
      'pos': {t: [constraint, ...]},   # constraints that require this agent's states/moves
    }
    For positive constraints addressed to OTHER agents, convert them to negative for THIS agent.
    """
    table = {'neg': {}, 'pos': {}}
    if not constraints:
        return table

    for c in constraints:
        t = c['timestep']
        is_pos = c.get('positive', False)
        # If this constraint targets this agent:
        if c.get('agent') == agent:
            key = 'pos' if is_pos else 'neg'
            table[key].setdefault(t, []).append(c)
        else:
            # Positive on someone else => implicit negative for me (disjoint splitting effect)
            if is_pos:
                neg_c = {'agent': agent, 'loc': c['loc'], 'timestep': t, 'positive': False}
                table['neg'].setdefault(t, []).append(neg_c)
            # Negative on someone else has no effect on me.
    return table


def is_constrained(curr_loc, next_loc, next_time, constraint_table):
    """
    Return True if the move (curr_loc -> next_loc) at next_time violates:
      - any negative constraint for this agent
      - any positive constraint for this agent (by not matching the required state/move)
    """
    neg = constraint_table['neg'].get(next_time, [])
    for c in neg:
        locs = c.get('loc', [])
        if len(locs) == 1:  # vertex forbid
            if next_loc == tuple(locs[0]):
                return True
        elif len(locs) == 2:  # edge forbid
            if curr_loc == tuple(locs[0]) and next_loc == tuple(locs[1]):
                return True

    # If there are any positive constraints at this time, the move must match at least one.
    pos = constraint_table['pos'].get(next_time, [])
    if pos:
        match = False
        for c in pos:
            locs = c.get('loc', [])
            if len(locs) == 1:  # must be at vertex
                if next_loc == tuple(locs[0]):
                    match = True
                    break
            elif len(locs) == 2:  # must traverse edge
                if curr_loc == tuple(locs[0]) and next_loc == tuple(locs[1]):
                    match = True
                    break
        if not match:
            return True

    return False


def a_star(my_map, start_loc, goal_loc, h_values, agent, constraints, max_timestep=None):
    # unchanged structure, just use the new table + is_constrained
    constraint_table = build_constraint_table(constraints, agent)

    # earliest goal time from negative constraints on goal (keep your existing logic)
    earliest_goal_t = 0
    for t, clist in constraint_table['neg'].items():
        for c in clist:
            if len(c.get('loc', [])) == 1 and tuple(c['loc'][0]) == goal_loc:
                earliest_goal_t = max(earliest_goal_t, t + 1)

    open_list = []
    closed = {}

    root = {'loc': start_loc, 'g_val': 0, 'h_val': h_values[start_loc], 'timestep': 0, 'parent': None}
    heapq.heappush(open_list, (root['g_val'] + root['h_val'], root['h_val'], root['loc'], root))
    closed[(root['loc'], root['timestep'])] = root

    neighbor_deltas = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]

    while open_list:
        _, _, _, curr = heapq.heappop(open_list)

        if max_timestep is not None and curr['timestep'] > max_timestep:
            continue

        # Goal test (respect earliest_goal_t)
        if curr['loc'] == goal_loc and curr['timestep'] >= earliest_goal_t:
            return get_path(curr)

        for dx, dy in neighbor_deltas:
            child_loc = (curr['loc'][0] + dx, curr['loc'][1] + dy)
            # bounds & obstacles
            if not (0 <= child_loc[0] < len(my_map) and 0 <= child_loc[1] < len(my_map[0])):
                continue
            if my_map[child_loc[0]][child_loc[1]]:
                continue

            next_time = curr['timestep'] + 1
            if max_timestep is not None and next_time > max_timestep:
                continue

            # constraints (neg + pos)
            if is_constrained(curr['loc'], child_loc, next_time, constraint_table):
                continue

            child = {
                'loc': child_loc,
                'g_val': curr['g_val'] + 1,
                'h_val': h_values[child_loc],
                'timestep': next_time,
                'parent': curr
            }
            key = (child['loc'], child['timestep'])
            if key not in closed or child['g_val'] + child['h_val'] < closed[key]['g_val'] + closed[key]['h_val']:
                closed[key] = child
                heapq.heappush(open_list, (child['g_val'] + child['h_val'], child['h_val'], child['loc'], child))

    return None
