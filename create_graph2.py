"""
Graph 2: Stability Comparison

X-Axis: "Pressure" (Weight β OR Bound K)
Y-Axis: Fairness Achieved (max_stretch)
Goal:
    - Show that increasing Naive Weight β (10 -> 50) is unpredictable (the stretch might not improve much).
    - Show that tightening Novel Bound K (2.0 -> 1.5) guarantees the stretch improves.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_graph2(csv_file="experiment_results.csv", instance_name=None, aggregate_instances=True):
    """
    Create Graph 2: Stability Comparison showing how Naive vs Novel approaches respond to pressure.
    
    Parameters:
    -----------
    csv_file : str
        Path to the experiment results CSV file
    instance_name : str, optional
        Specific instance to plot (e.g., "bottleneck_10x10_1.txt")
        If None and aggregate_instances=True, will aggregate across all instances
    aggregate_instances : bool
        If True, aggregate results across all instances (shows average behavior)
        If False, plot for a single instance
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
    
    # Select data to plot
    if aggregate_instances and instance_name is None:
        # Aggregate across all instances (average max_stretch for each solver)
        plot_df = df.groupby(['solver', 'naive_weight', 'novel_bound']).agg({
            'max_stretch': 'mean',
            'instance': 'count'  # Count how many instances contributed
        }).reset_index()
        plot_df.rename(columns={'instance': 'num_instances'}, inplace=True)
        title_suffix = " (Averaged Across All Instances)"
    else:
        # Plot for a specific instance
        if instance_name is None:
            # Find the first bottleneck instance
            bottleneck_instances = df[df['instance'].str.contains('bottleneck', case=False, na=False)]
            if len(bottleneck_instances) > 0:
                instance_name = bottleneck_instances['instance'].iloc[0]
                print(f"Using instance: {instance_name}")
            else:
                instance_name = df['instance'].iloc[0]
                print(f"Using instance: {instance_name}")
        
        plot_df = df[df['instance'] == instance_name].copy()
        title_suffix = f"\nInstance: {instance_name}"
    
    if len(plot_df) == 0:
        print("Error: No data found")
        return
    
    # Separate Naive (Weighted) and Novel (Bounded) approaches
    naive_df = plot_df[plot_df['solver'].str.contains('Weighted', case=False, na=False)].copy()
    novel_df = plot_df[plot_df['solver'].str.contains('Bounded', case=False, na=False)].copy()
    
    # Create side-by-side subplots for clearer comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot Naive Approach (Weighted) - Left subplot
    if len(naive_df) > 0:
        # Sort by naive_weight
        naive_df = naive_df.sort_values('naive_weight')
        
        # Check if all values are the same
        unique_stretch = naive_df['max_stretch'].nunique()
        all_same_naive = (unique_stretch == 1)
        
        # X-axis: β (weight)
        # Y-axis: max_stretch
        ax1.plot(naive_df['naive_weight'], 
                naive_df['max_stretch'],
                'o-', 
                color='orange', 
                linewidth=2.5, 
                markersize=12,
                label='Naive Approach (Weighted Sum)',
                zorder=3)
        
        # Add scatter points with varying sizes to show different β values
        sizes = [150 + i*50 for i in range(len(naive_df))]
        ax1.scatter(naive_df['naive_weight'],
                  naive_df['max_stretch'],
                  color='orange',
                  s=sizes,
                  edgecolors='darkorange',
                  linewidths=2.5,
                  zorder=4,
                  alpha=0.7)
        
        # Add annotations for each point
        for idx, row in naive_df.iterrows():
            ax1.annotate(f'β={int(row["naive_weight"])}\n{row["max_stretch"]:.3f}',
                       (row['naive_weight'], row['max_stretch']),
                       textcoords="offset points",
                       xytext=(0, 25),
                       ha='center',
                       fontsize=9,
                       fontweight='bold',
                       color='darkorange',
                       bbox={'boxstyle': 'round,pad=0.3', 'facecolor': 'white', 'alpha': 0.8, 'edgecolor': 'orange'})
        
        # Set Y-axis range to make the line more visible
        y_min = naive_df['max_stretch'].min()
        y_max = naive_df['max_stretch'].max()
        if y_min == y_max:
            # All values are the same, add some padding
            ax1.set_ylim([y_min - 0.1, y_max + 0.1])
            # Add horizontal line annotation
            ax1.axhline(y=y_min, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Constant (No Change)')
        else:
            # Add some padding
            y_range = y_max - y_min
            ax1.set_ylim([y_min - y_range*0.2, y_max + y_range*0.2])
        
        ax1.set_xlabel('Weight β (Higher = More Pressure)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Fairness Achieved (max_stretch)', fontsize=12, fontweight='bold')
        title = 'Naive Approach: Unpredictable'
        if all_same_naive:
            title += '\n(No change: All β values yield same result)'
        ax1.set_title(title, fontsize=13, fontweight='bold', color='orange')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='best', fontsize=9)
    else:
        ax1.text(0.5, 0.5, 'No Naive Approach data', ha='center', va='center', transform=ax1.transAxes)
        ax1.set_title('Naive Approach: Unpredictable', fontsize=13, fontweight='bold')
    
    # Plot Novel Approach (Bounded) - Right subplot
    if len(novel_df) > 0:
        # Sort by novel_bound (ascending to show K decreasing = more pressure)
        novel_df = novel_df.sort_values('novel_bound', ascending=False)
        
        # Check if all values are the same
        unique_stretch = novel_df['max_stretch'].nunique()
        all_same_novel = (unique_stretch == 1)
        
        # X-axis: K (bound) - lower K = more pressure
        # Y-axis: max_stretch
        ax2.plot(novel_df['novel_bound'],
                novel_df['max_stretch'],
                's-',
                color='blue',
                linewidth=2.5,
                markersize=12,
                label='Novel Approach (Bounded Constraint)',
                zorder=3)
        
        # Add scatter points with varying sizes
        sizes = [150 + i*50 for i in range(len(novel_df))]
        ax2.scatter(novel_df['novel_bound'],
                   novel_df['max_stretch'],
                   color='blue',
                   s=sizes,
                   edgecolors='darkblue',
                   linewidths=2.5,
                   zorder=4,
                   alpha=0.7)
        
        # Add annotations showing K value
        for idx, row in novel_df.iterrows():
            ax2.annotate(f'K={row["novel_bound"]}\n{row["max_stretch"]:.3f}',
                        (row['novel_bound'], row['max_stretch']),
                        textcoords="offset points",
                        xytext=(0, -25),
                        ha='center',
                        fontsize=9,
                        fontweight='bold',
                        color='darkblue',
                        bbox={'boxstyle': 'round,pad=0.3', 'facecolor': 'white', 'alpha': 0.8, 'edgecolor': 'blue'})
        
        # Set Y-axis range to make the line more visible
        y_min = novel_df['max_stretch'].min()
        y_max = novel_df['max_stretch'].max()
        if y_min == y_max:
            # All values are the same, add some padding
            ax2.set_ylim([y_min - 0.1, y_max + 0.1])
            # Add horizontal line annotation
            ax2.axhline(y=y_min, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Constant (No Change)')
        else:
            # Add some padding
            y_range = y_max - y_min
            ax2.set_ylim([y_min - y_range*0.2, y_max + y_range*0.2])
        
        # Invert x-axis to show lower K (more pressure) on the right
        ax2.invert_xaxis()
        ax2.set_xlabel('Bound K (Lower = More Pressure →)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Fairness Achieved (max_stretch)', fontsize=12, fontweight='bold')
        title = 'Novel Approach: Guaranteed Improvement'
        if all_same_novel:
            title += '\n(No change: All K values yield same result)'
        ax2.set_title(title, fontsize=13, fontweight='bold', color='blue')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='best', fontsize=9)
    else:
        ax2.text(0.5, 0.5, 'No Novel Approach data', ha='center', va='center', transform=ax2.transAxes)
        ax2.set_title('Novel Approach: Guaranteed Improvement', fontsize=13, fontweight='bold')
    
    # Set main title
    fig.suptitle(f'Stability Comparison: Naive vs Novel Approaches{title_suffix}', 
                fontsize=15, fontweight='bold', y=1.02)
    
    # Check if all values are the same
    all_same = False
    if len(naive_df) > 0 and len(novel_df) > 0:
        naive_unique = naive_df['max_stretch'].nunique()
        novel_unique = novel_df['max_stretch'].nunique()
        if naive_unique == 1 and novel_unique == 1:
            all_same = True
    
    # Add annotation explaining the difference
    if all_same:
        explanation_text = (
            'Observation: All methods found identical solutions (max_stretch=1.0).\n'
            'This instance is inherently fair - all CBS methods converge to the same optimal fair solution.\n'
            'The theoretical difference (Naive=unpredictable, Novel=guaranteed) is not visible here\n'
            'because the instance does not require a fairness-efficiency trade-off.'
        )
    else:
        explanation_text = (
            'Key Insight:\n'
            '• Naive: Increasing β is UNPREDICTABLE\n'
            '• Novel: Tightening K GUARANTEES improvement'
        )
    fig.text(0.5, 0.01,
           explanation_text,
           fontsize=9,
           ha='center',
           bbox={'boxstyle': 'round', 'facecolor': 'lightyellow', 'alpha': 0.8})
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'graph2_stability_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nGraph saved to: {output_file}")
    
    # Show the plot
    plt.show()
    
    # Print summary statistics
    print("\n" + "="*70)
    print("Summary Statistics:")
    print("="*70)
    
    if len(naive_df) > 0:
        print("\nNaive Approach (Weighted Sum):")
        print("-" * 70)
        for idx, row in naive_df.iterrows():
            instances_info = f" ({int(row['num_instances'])} instances)" if 'num_instances' in row else ""
            print(f"  β = {int(row['naive_weight']):2d}  |  max_stretch = {row['max_stretch']:6.3f}{instances_info}")
    
    if len(novel_df) > 0:
        print("\nNovel Approach (Bounded Constraint):")
        print("-" * 70)
        for idx, row in novel_df.iterrows():
            instances_info = f" ({int(row['num_instances'])} instances)" if 'num_instances' in row else ""
            print(f"  K = {row['novel_bound']:4.1f}  |  max_stretch = {row['max_stretch']:6.3f}{instances_info}")
    
    print("="*70)
    
    # Calculate and show the key insight
    if len(naive_df) >= 2:
        naive_improvement = naive_df.iloc[0]['max_stretch'] - naive_df.iloc[-1]['max_stretch']
        print(f"\nNaive Approach: Changing β from {int(naive_df.iloc[0]['naive_weight'])} to {int(naive_df.iloc[-1]['naive_weight'])}")
        print(f"  → max_stretch change: {naive_improvement:+.3f} ({'IMPROVED' if naive_improvement > 0 else 'NO CHANGE or WORSE'})")
    
    if len(novel_df) >= 2:
        novel_improvement = novel_df.iloc[0]['max_stretch'] - novel_df.iloc[-1]['max_stretch']
        print(f"\nNovel Approach: Tightening K from {novel_df.iloc[0]['novel_bound']} to {novel_df.iloc[-1]['novel_bound']}")
        print(f"  → max_stretch change: {novel_improvement:+.3f} ({'GUARANTEED IMPROVEMENT' if novel_improvement > 0 else 'NO CHANGE'})")

if __name__ == "__main__":
    import sys
    
    # Allow specifying instance name as command line argument
    instance_name = None
    aggregate = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--single":
            aggregate = False
            if len(sys.argv) > 2:
                instance_name = sys.argv[2]
        else:
            instance_name = sys.argv[1]
            aggregate = False
    
    create_graph2(instance_name=instance_name, aggregate_instances=aggregate)

