"""
Graph 1: The "Price of Fairness" (Pareto Frontier)

X-Axis: Fairness (max_stretch)
Y-Axis: Inefficiency (soc)
Goal: Show that as we force Fairness (moving left on X), the Cost (Y) increases.
Plotting: Filter for one specific map (e.g., Bottleneck 1). 
          Plot points for CBS_Standard vs. CBS_Bounded_2.0, 1.5, 1.2.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_graph1(csv_file="experiment_results.csv", instance_name=None):
    """
    Create Graph 1: Pareto Frontier showing the trade-off between fairness and efficiency.
    
    Parameters:
    -----------
    csv_file : str
        Path to the experiment results CSV file
    instance_name : str, optional
        Specific instance to plot (e.g., "bottleneck_10x10_1.txt")
        If None, will use the first bottleneck instance found
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
    
    # Select the instance to plot
    if instance_name is None:
        # Find the first bottleneck instance
        bottleneck_instances = df[df['instance'].str.contains('bottleneck', case=False, na=False)]
        if len(bottleneck_instances) > 0:
            instance_name = bottleneck_instances['instance'].iloc[0]
            print(f"Using instance: {instance_name}")
        else:
            # Fall back to first available instance
            instance_name = df['instance'].iloc[0]
            print(f"No bottleneck instance found. Using: {instance_name}")
    
    # Filter for the selected instance
    instance_df = df[df['instance'] == instance_name].copy()
    
    if len(instance_df) == 0:
        print(f"Error: No data found for instance '{instance_name}'")
        print(f"Available instances: {df['instance'].unique()}")
        return
    
    # Filter for the solvers we want to plot
    solvers_to_plot = ['CBS_Standard', 'CBS_Bounded_2.0', 'CBS_Bounded_1.5', 'CBS_Bounded_1.2']
    plot_df = instance_df[instance_df['solver'].isin(solvers_to_plot)].copy()
    
    if len(plot_df) == 0:
        print(f"Error: No data found for the specified solvers in instance '{instance_name}'")
        print(f"Available solvers: {instance_df['solver'].unique()}")
        return
    
    # Sort by max_stretch for better visualization
    plot_df = plot_df.sort_values('max_stretch')
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Define colors and markers for each solver
    solver_styles = {
        'CBS_Standard': {'color': 'red', 'marker': 'o', 'label': 'CBS Standard (Unfair Baseline)', 'size': 100},
        'CBS_Bounded_2.0': {'color': 'blue', 'marker': 's', 'label': 'CBS Bounded (K=2.0)', 'size': 100},
        'CBS_Bounded_1.5': {'color': 'green', 'marker': '^', 'label': 'CBS Bounded (K=1.5)', 'size': 100},
        'CBS_Bounded_1.2': {'color': 'purple', 'marker': 'D', 'label': 'CBS Bounded (K=1.2)', 'size': 100},
    }
    
    # Plot each solver
    for solver in solvers_to_plot:
        solver_data = plot_df[plot_df['solver'] == solver]
        if len(solver_data) > 0:
            style = solver_styles.get(solver, {'color': 'gray', 'marker': 'o', 'label': solver, 'size': 100})
            plt.scatter(
                solver_data['max_stretch'],
                solver_data['soc'],
                color=style['color'],
                marker=style['marker'],
                s=style['size'],
                label=style['label'],
                edgecolors='black',
                linewidths=1.5,
                zorder=3
            )
    
    # Draw lines connecting points to show the Pareto frontier trend
    # Sort by max_stretch to draw the line
    sorted_df = plot_df.sort_values('max_stretch')
    if len(sorted_df) > 1:
        plt.plot(
            sorted_df['max_stretch'],
            sorted_df['soc'],
            '--',
            color='gray',
            alpha=0.5,
            linewidth=1,
            zorder=1,
            label='Pareto Frontier'
        )
    
    # Customize the plot
    plt.xlabel('Fairness (max_stretch)', fontsize=12, fontweight='bold')
    plt.ylabel('Inefficiency (Sum of Costs)', fontsize=12, fontweight='bold')
    plt.title(f'Price of Fairness: Pareto Frontier\nInstance: {instance_name}', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(loc='best', fontsize=10)
    
    # Add annotation explaining the trade-off
    plt.text(0.02, 0.98, 
             'Lower max_stretch = More Fair\nHigher SOC = Less Efficient',
             transform=plt.gca().transAxes,
             fontsize=9,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Invert x-axis to show "more fair" moving right (optional - comment out if you prefer)
    # Actually, let's keep it as is - lower values on left (more fair), higher on right (less fair)
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'graph1_pareto_frontier.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nGraph saved to: {output_file}")
    
    # Show the plot
    plt.show()
    
    # Print summary statistics
    print("\n" + "="*60)
    print("Summary Statistics:")
    print("="*60)
    for solver in solvers_to_plot:
        solver_data = plot_df[plot_df['solver'] == solver]
        if len(solver_data) > 0:
            row = solver_data.iloc[0]
            print(f"{solver:20s} | max_stretch: {row['max_stretch']:6.2f} | SOC: {row['soc']:8.2f}")
    print("="*60)

if __name__ == "__main__":
    import sys
    
    # Allow specifying instance name as command line argument
    instance_name = None
    if len(sys.argv) > 1:
        instance_name = sys.argv[1]
    
    create_graph1(instance_name=instance_name)

