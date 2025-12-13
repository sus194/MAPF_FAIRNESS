import random
import os
import collections

# --- HELPER FUNCTIONS ---
def bfs_is_connected(my_map):
    rows = len(my_map)
    cols = len(my_map[0])
    free_cells = [(r, c) for r in range(rows) for c in range(cols) if not my_map[r][c]]
    if not free_cells: return False
    start = free_cells[0]
    queue = collections.deque([start])
    visited = set([start])
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not my_map[nr][nc] and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
    return len(visited) == len(free_cells)

def save_instance(filename, my_map, starts, goals):
    with open(filename, 'w') as f:
        rows = len(my_map)
        cols = len(my_map[0])
        f.write(f"{rows} {cols}\n")
        for r in range(rows):
            line = ""
            for c in range(cols):
                line += "@" if my_map[r][c] else "."
            f.write(line + "\n")
        f.write(f"{len(starts)}\n")
        for i in range(len(starts)):
            f.write(f"{starts[i][0]} {starts[i][1]} {goals[i][0]} {goals[i][1]}\n")

# --- MAP GENERATORS ---

def generate_asymmetric_conflict():
    """ 4 Agents vs 1 Agent (Medium Intersection) """
    rows, cols = 8, 8
    my_map = [[False for _ in range(cols)] for _ in range(rows)]
    for r in [0, 1, 6, 7]:
        for c in range(cols):
            if c != 3 and c != 4: my_map[r][c] = True
    
    starts = []
    goals = []
    # 4 Agents Left->Right
    for s, g in [((3,0),(3,7)), ((4,0),(4,7)), ((3,1),(3,6)), ((4,1),(4,6))]:
        starts.append(s); goals.append(g)
    # 1 Agent Top->Bottom
    starts.append((0, 3)); goals.append((7, 4))
    
    return my_map, starts, goals

def generate_random_scalability():
    """ 12 Agents on 12x12 Map (Medium Density) """
    while True:
        my_map = []
        for r in range(12):
            row = [random.random() < 0.1 for _ in range(12)]
            my_map.append(row)
        
        if bfs_is_connected(my_map):
            free = [(r, c) for r in range(12) for c in range(12) if not my_map[r][c]]
            if len(free) >= 24:
                pts = random.sample(free, 24)
                return my_map, pts[:12], pts[12:]

def generate_airport_mini():
    """ 4 Agents on 16x16 Airport """
    my_map = [[True for _ in range(16)] for _ in range(16)]
    for r in range(7, 9): # Main Taxiway
        for c in range(1, 15): my_map[r][c] = False
    
    terminals = [4, 8, 12]
    gate_locs = []
    for c in terminals:
        for r in range(2, 7): my_map[r][c] = False
        gate_locs.append((2, c))
        for r in range(9, 14): my_map[r][c] = False
        gate_locs.append((13, c))
        
    runway_L, runway_R = (7, 1), (8, 14)
    if not bfs_is_connected(my_map): return generate_airport_mini() # Retry if broken
    
    all_spots = gate_locs + [runway_L, runway_R]
    if len(all_spots) < 8: return generate_airport_mini()

    pts = random.sample(all_spots, 8)
    return my_map, pts[:4], pts[4:]

# --- MAIN ---
def main():
    if not os.path.exists('instances'): os.makedirs('instances')
    print("Generating instances...")

    m1, s1, g1 = generate_asymmetric_conflict()
    save_instance("instances/asymmetric_conflict.txt", m1, s1, g1)
    
    m2, s2, g2 = generate_random_scalability()
    save_instance("instances/random_scalability.txt", m2, s2, g2)
    
    m3, s3, g3 = generate_airport_mini()
    save_instance("instances/airport_mini.txt", m3, s3, g3)
    
    print("Created 3 instances: asymmetric, random, airport.")

if __name__ == "__main__":
    main()