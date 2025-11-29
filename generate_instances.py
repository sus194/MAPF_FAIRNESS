import random
import os

def generate_random_map(rows, cols, obstacle_prob):
    """Generates a grid with random obstacles."""
    my_map = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if random.random() < obstacle_prob:
                row.append(True)  # True = Obstacle (@)
            else:
                row.append(False) # False = Free (.)
        my_map.append(row)
    return my_map

def generate_bottleneck_map(rows, cols, gap_width=1):
    """
    Generates a map with a vertical wall in the middle and a small gap.
    This forces agents to queue, testing fairness logic.
    """
    my_map = [[False for _ in range(cols)] for _ in range(rows)]
    mid_col = cols // 2
    
    # Build the wall
    for r in range(rows):
        my_map[r][mid_col] = True
        
    # Punch the gap
    start_gap = (rows - gap_width) // 2
    for r in range(start_gap, start_gap + gap_width):
        my_map[r][mid_col] = False
        
    return my_map

def get_valid_locations(my_map):
    """Returns a list of all free (x, y) coordinates."""
    locs = []
    for r in range(len(my_map)):
        for c in range(len(my_map[0])):
            if not my_map[r][c]:
                locs.append((r, c))
    return locs

def generate_agents(my_map, num_agents):
    """Generates unique start and goal positions for N agents."""
    free_cells = get_valid_locations(my_map)
    if len(free_cells) < 2 * num_agents:
        raise ValueError("Map is too small/crowded for this many agents.")
    
    # Pick 2*N unique locations (N starts + N goals)
    samples = random.sample(free_cells, 2 * num_agents)
    starts = samples[:num_agents]
    goals = samples[num_agents:]
    return starts, goals

def save_instance(filename, my_map, starts, goals):
    with open(filename, 'w') as f:
        # 1. Dimensions
        rows = len(my_map)
        cols = len(my_map[0])
        f.write(f"{rows} {cols}\n")
        
        # 2. Map Grid
        for r in range(rows):
            line = ""
            for c in range(cols):
                line += "@" if my_map[r][c] else "."
            f.write(line + "\n")
            
        # 3. Agents
        f.write(f"{len(starts)}\n")
        for i in range(len(starts)):
            f.write(f"{starts[i][0]} {starts[i][1]} {goals[i][0]} {goals[i][1]}\n")

def main():
    if not os.path.exists('instances'):
        os.makedirs('instances')
        
    print("Generating instances...")

    # --- SET 1: Random Maps (General Performance) ---
    # 8x8 grid, 20% obstacles, 4 agents
    for i in range(1, 4):
        my_map = generate_random_map(8, 8, 0.2)
        starts, goals = generate_agents(my_map, 4)
        fname = f"instances/random_8x8_{i}.txt"
        save_instance(fname, my_map, starts, goals)
        print(f"Created {fname}")

    # --- SET 2: Bottleneck Maps (The Fairness Test) ---
    # 10x10 grid, 1-tile gap, 4 agents crossing sides
    for i in range(1, 4):
        my_map = generate_bottleneck_map(10, 10, gap_width=1)
        
        # Manually force agents to cross the bottleneck for maximum conflict
        # Left side starts, Right side goals
        starts = [(r, 0) for r in range(4)] 
        goals = [(9-r, 9) for r in range(4)]
        
        fname = f"instances/bottleneck_10x10_{i}.txt"
        save_instance(fname, my_map, starts, goals)
        print(f"Created {fname}")

if __name__ == "__main__":
    main()