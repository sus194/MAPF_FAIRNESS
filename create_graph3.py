"""
Graph 3: Scalability

X-Axis: Map Type (Random vs. Bottleneck)
Y-Axis: cpu_time
Goal: Show that Fairness is "cheap" on Random maps but "expensive" on Bottleneck maps 
      (Bounded solvers might take longer).
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_graph3(csv_file="experiment_results.csv"):
    """
    Create Graph 3: Scalability comparison showing CPU time across map types.
    
    Parameters:
    -----------
    csv_file : str
        Path to the experiment results CSV file
    """
    # Load the data
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file}")
        print("Please run 'python run_experiments.py' first to generate the data.")
        return
    
    # Filter for successful experiments only
    df = df[df['success'] == True].copy()
    
    if len(df) == 0:
        print("Error: No successful experiments found in the CSV file.")
        return
    
    # Categorize instances by map type
    df['map_type'] = df['instance'].apply(
        lambda x: 'Bottleneck' if 'bottleneck' in x.lower() 
        else 'Random' if 'random' in x.lower() 
        else 'Other'
    )
    
    # Filter out 'Other' category if we only want Random vs Bottleneck
    df = df[df['map_type'].isin(['Random', 'Bottleneck'])].copy()
    
    if len(df) == 0:
        print("Error: No Random or Bottleneck instances found.")
        return
    
    # Select solvers to compare
    # Focus on key solvers: Standard, Weighted, and Bounded variants
    solvers_to_plot = [
        'CBS_Standard',
        'CBS_Weighted_10',
        'CBS_Weighted_50',
        'CBS_Bounded_2.0',
        'CBS_Bounded_1.5',
        'CBS_Bounded_1.2'
    ]
    
    # Filter for selected solvers
    plot_df = df[df['solver'].isin(solvers_to_plot)].copy()
    
    if len(plot_df) == 0:
        print("Error: No data found for the specified solvers.")
        return
    
    # Handle zero or very small cpu_time values (replace 0 with a small value for log scale if needed)
    plot_df['cpu_time'] = pd.to_numeric(plot_df['cpu_time'], errors='coerce')
    plot_df = plot_df[plot_df['cpu_time'].notna()].copy()
    
    # Aggregate: calculate mean cpu_time for each solver and map type
    # Group by solver and map_type, then calculate mean and std
    summary_df = plot_df.groupby(['solver', 'map_type']).agg({
        'cpu_time': ['mean', 'std', 'count']
    }).reset_index()
    summary_df.columns = ['solver', 'map_type', 'mean_cpu_time', 'std_cpu_time', 'count']
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Prepare data for grouped bar chart
    map_types = ['Random', 'Bottleneck']
    x = np.arange(len(map_types))
    width = 0.13  # Width of bars
    
    # Define colors for each solver
    solver_colors = {
        'CBS_Standard': '#FF6B6B',      # Red
        'CBS_Weighted_10': '#FFA07A',    # Light Salmon
        'CBS_Weighted_50': '#FF8C00',    # Dark Orange
        'CBS_Bounded_2.0': '#4ECDC4',    # Turquoise
        'CBS_Bounded_1.5': '#45B7D1',   # Sky Blue
        'CBS_Bounded_1.2': '#2E86AB',   # Dark Blue
    }
    
    solver_labels = {
        'CBS_Standard': 'Standard',
        'CBS_Weighted_10': 'Weighted (β=10)',
        'CBS_Weighted_50': 'Weighted (β=50)',
        'CBS_Bounded_2.0': 'Bounded (K=2.0)',
        'CBS_Bounded_1.5': 'Bounded (K=1.5)',
        'CBS_Bounded_1.2': 'Bounded (K=1.2)',
    }
    
    # Plot bars for each solver
    offset = -(len(solvers_to_plot) - 1) * width / 2
    bars = []
    
    for i, solver in enumerate(solvers_to_plot):
        solver_data = summary_df[summary_df['solver'] == solver]
        
        means = []
        stds = []
        
        for map_type in map_types:
            mt_data = solver_data[solver_data['map_type'] == map_type]
            if len(mt_data) > 0:
                means.append(mt_data['mean_cpu_time'].iloc[0])
                stds.append(mt_data['std_cpu_time'].iloc[0])
            else:
                means.append(0)
                stds.append(0)
        
        # Create bars
        bar = ax.bar(x + offset, means, width, 
                    yerr=stds if any(s > 0 for s in stds) else None,
                    label=solver_labels[solver],
                    color=solver_colors.get(solver, 'gray'),
                    edgecolor='black',
                    linewidth=1,
                    alpha=0.8,
                    capsize=3)
        bars.append(bar)
        offset += width
    
    # Customize the plot
    ax.set_xlabel('Map Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('CPU Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Scalability: CPU Time Comparison Across Map Types', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(map_types)
    ax.legend(loc='upper left', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add annotation explaining the insight
    insight_text = (
        'Key Insight:\n'
        '• Fairness is "cheap" on Random maps\n'
        '• Fairness is "expensive" on Bottleneck maps\n'
        '  (Bounded solvers with tighter bounds take longer)'
    )
    ax.text(0.02, 0.98,
           insight_text,
           transform=ax.transAxes,
           fontsize=10,
           verticalalignment='top',
           bbox={'boxstyle': 'round', 'facecolor': 'lightyellow', 'alpha': 0.8})
    
    # Use log scale if there's a large range in cpu_time
    if plot_df['cpu_time'].max() / (plot_df['cpu_time'].min() + 1e-10) > 100:
        ax.set_yscale('log')
        ax.set_ylabel('CPU Time (seconds, log scale)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'graph3_scalability.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nGraph saved to: {output_file}")
    
    # Show the plot
    plt.show()
    
    # Print summary statistics
    print("\n" + "="*80)
    print("Summary Statistics: Average CPU Time (seconds)")
    print("="*80)
    
    for map_type in map_types:
        print(f"\n{map_type} Maps:")
        print("-" * 80)
        mt_data = summary_df[summary_df['map_type'] == map_type].sort_values('mean_cpu_time', ascending=False)
        for idx, row in mt_data.iterrows():
            solver_label = solver_labels.get(row['solver'], row['solver'])
            print(f"  {solver_label:25s} | Mean: {row['mean_cpu_time']:10.6f} | "
                  f"Std: {row['std_cpu_time']:10.6f} | Count: {int(row['count'])}")
    
    print("\n" + "="*80)
    
    # Calculate and show the key insight: ratio of Bottleneck to Random
    print("\nKey Insight: Bottleneck vs Random CPU Time Ratio")
    print("-" * 80)
    for solver in solvers_to_plot:
        solver_data = summary_df[summary_df['solver'] == solver]
        bottleneck_data = solver_data[solver_data['map_type'] == 'Bottleneck']
        random_data = solver_data[solver_data['map_type'] == 'Random']
        
        if len(bottleneck_data) > 0 and len(random_data) > 0:
            bottleneck_time = bottleneck_data['mean_cpu_time'].iloc[0]
            random_time = random_data['mean_cpu_time'].iloc[0]
            if random_time > 0:
                ratio = bottleneck_time / random_time
                solver_label = solver_labels.get(solver, solver)
                print(f"  {solver_label:25s} | Ratio: {ratio:6.2f}x "
                      f"(Bottleneck: {bottleneck_time:.6f}s, Random: {random_time:.6f}s)")
    
    print("="*80)

if __name__ == "__main__":
    create_graph3()

