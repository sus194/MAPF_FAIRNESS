import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# 1. Load Data
if not os.path.exists('experiment_results.csv'):
    print("Error: 'experiment_results.csv' not found.")
    exit()

df = pd.read_csv('experiment_results.csv')

# --- PRE-PROCESSING ---
# 1. Handle Timeouts: If success=False, set CPU time to 60s (or max) for visualization
df.loc[df['success'] == False, 'cpu_time'] = 60.0

# 2. Fix Zero CPU Time: Log scale can't handle 0, so make it tiny (0.001s)
df['cpu_time'] = df['cpu_time'].replace(0, 0.001)

# 3. Rename Solvers for cleaner legends
def rename_solver(name):
    if name == 'Prioritized': return 'Prioritized (Baseline)'
    if name == 'CBS_Standard': return 'CBS Standard (Optimal)'
    if 'Weighted' in name: return 'Naive (Weighted)'
    if 'Bounded' in name: return 'Novel (Bounded)' + name.split('_')[-1]
    return name

df['Solver_Label'] = df['solver'].apply(rename_solver)

# 4. Categorize Solvers
def get_category(name):
    if 'Prioritized' in name: return 'Baseline'
    if 'Standard' in name: return 'Baseline'
    if 'Weighted' in name: return 'Naive'
    if 'Bounded' in name: return 'Novel'
    return 'Other'

df['Category'] = df['solver'].apply(get_category)

sns.set_theme(style="whitegrid")

# ==========================================
# GRAPH 1: The "Price of Fairness" (Pareto)
# ==========================================
# Filter for the Asymmetric map where the trade-off happened
pareto_df = df[df['instance'].str.contains('asymmetric') & (df['success'] == True)].copy()

plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=pareto_df, 
    x='max_stretch', 
    y='soc', 
    hue='Category', 
    style='Category', 
    s=200, # Marker size
    palette='bright'
)

plt.title('Graph 1: Price of Fairness (Pareto Frontier)', fontsize=14)
plt.xlabel('Fairness (Max Stretch) [Lower is Better]', fontsize=12)
plt.ylabel('Inefficiency (Sum of Costs) [Lower is Better]', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Approach')
plt.grid(True, linestyle='--')
plt.tight_layout()
plt.savefig('graph1_pareto.png')
print("Generated graph1_pareto.png")
plt.show()

# ==========================================
# GRAPH 2: Stability (Novel vs. Naive)
# ==========================================
# We want to see how the solver behaves when we tighten the constraints
# Filter for Asymmetric map again
stab_df = df[df['instance'].str.contains('asymmetric')].copy()
stab_df = stab_df[stab_df['solver'].str.contains('Bounded') | stab_df['solver'].str.contains('Weighted')]

plt.figure(figsize=(10, 6))
# Create a bar chart that shows Max Stretch. If it failed (NaN), fill with 0 or skip
sns.barplot(
    data=stab_df, 
    x='solver', 
    y='max_stretch', 
    hue='Category', 
    palette='muted'
)

plt.title('Graph 2: Stability & Constraints', fontsize=14)
plt.ylabel('Fairness Achieved (Max Stretch)', fontsize=12)
plt.xlabel('Solver Configuration', fontsize=12)
plt.xticks(rotation=45)
plt.axhline(y=1.28, color='r', linestyle='--', label='Theoretical Limit (1.28)')
plt.legend()
plt.tight_layout()
plt.savefig('graph2_stability.png')
print("Generated graph2_stability.png")
plt.show()

# ==========================================
# GRAPH 3: Scalability (CPU Time)
# ==========================================
# Compare "Easy" (Airport) vs "Hard" (Random Dense)
# We exclude the asymmetric map here to focus on map size/density
scale_df = df[~df['instance'].str.contains('asymmetric')].copy()

plt.figure(figsize=(10, 6))
barplot = sns.barplot(
    data=scale_df, 
    x='instance', 
    y='cpu_time', 
    hue='Category',
    palette='magma'
)

plt.title('Graph 3: Scalability (Computational Cost)', fontsize=14)
plt.ylabel('CPU Time (Seconds) - Log Scale', fontsize=12)
plt.xlabel('Map Difficulty', fontsize=12)
plt.yscale('log') # Crucial for showing the massive difference
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

# Add "Timeout" labels for failed runs
for p, row in zip(barplot.patches, scale_df.itertuples()):
    if not row.success: # If success is False
        barplot.annotate("Timeout", 
                         (p.get_x() + p.get_width() / 2., 50), # Position at 50s mark
                         ha='center', va='center', color='white', rotation=90, fontweight='bold')

plt.tight_layout()
plt.savefig('graph3_scalability.png')
print("Generated graph3_scalability.png")
plt.show()