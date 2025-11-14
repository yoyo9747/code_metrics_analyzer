"""
COCOMO Results Visualization Script
Generates charts and visualizations for the report
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Try to import seaborn for better styling
try:
    import seaborn as sns
    sns.set_style("whitegrid")
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    print("Seaborn not available, using default matplotlib styling")


def load_results(filename='cocomo_results.json'):
    """Load COCOMO results from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)


def create_comparison_chart(results):
    """Create comprehensive comparison chart"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('COCOMO Analysis - Comparative Overview', fontsize=16, fontweight='bold')
    
    projects = [r['project_name'] for r in results]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # 1. KLOC Comparison
    ax = axes[0, 0]
    kloc_values = [r['kloc'] for r in results]
    bars = ax.bar(projects, kloc_values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('KLOC', fontsize=10)
    ax.set_title('Project Size (KLOC)', fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars, kloc_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}',
                ha='center', va='bottom', fontsize=9)
    
    # 2. Effort Comparison
    ax = axes[0, 1]
    basic_effort = [r['basic_cocomo']['effort_pm'] for r in results]
    inter_effort = [r['intermediate_cocomo']['effort_pm'] for r in results]
    
    x = np.arange(len(projects))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, basic_effort, width, label='Basic', 
                   color='#3498db', alpha=0.7, edgecolor='black')
    bars2 = ax.bar(x + width/2, inter_effort, width, label='Intermediate',
                   color='#e74c3c', alpha=0.7, edgecolor='black')
    
    ax.set_ylabel('Person-Months', fontsize=10)
    ax.set_title('Effort Estimation', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(projects, rotation=45, ha='right')
    ax.legend()
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=8)
    
    # 3. Development Time
    ax = axes[0, 2]
    basic_time = [r['basic_cocomo']['time_months'] for r in results]
    inter_time = [r['intermediate_cocomo']['time_months'] for r in results]
    
    bars1 = ax.bar(x - width/2, basic_time, width, label='Basic',
                   color='#2ecc71', alpha=0.7, edgecolor='black')
    bars2 = ax.bar(x + width/2, inter_time, width, label='Intermediate',
                   color='#f39c12', alpha=0.7, edgecolor='black')
    
    ax.set_ylabel('Months', fontsize=10)
    ax.set_title('Development Time', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(projects, rotation=45, ha='right')
    ax.legend()
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=8)
    
    # 4. Team Size
    ax = axes[1, 0]
    team_sizes = [r['intermediate_cocomo']['avg_people'] for r in results]
    bars = ax.bar(projects, team_sizes, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Average Team Size', fontsize=10)
    ax.set_title('Required Team Size', fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='1 Person')
    ax.legend()
    
    # Add value labels
    for bar, value in zip(bars, team_sizes):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}',
                ha='center', va='bottom', fontsize=9)
    
    # 5. Productivity
    ax = axes[1, 1]
    productivity = [r['intermediate_cocomo']['productivity'] for r in results]
    bars = ax.bar(projects, productivity, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('KLOC/Person-Month', fontsize=10)
    ax.set_title('Productivity', fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, productivity):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}',
                ha='center', va='bottom', fontsize=9)
    
    # 6. EAF Impact
    ax = axes[1, 2]
    eaf_values = [r['intermediate_cocomo']['eaf'] for r in results]
    bars = ax.bar(projects, eaf_values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('EAF Value', fontsize=10)
    ax.set_title('Effort Adjustment Factor', fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.axhline(y=1.0, color='red', linestyle='--', alpha=0.5, label='Nominal (1.0)')
    ax.legend()
    
    # Add value labels and percentage
    for bar, value in zip(bars, eaf_values):
        height = bar.get_height()
        impact = (value - 1.0) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}\n({impact:+.1f}%)',
                ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig('cocomo_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: cocomo_comparison.png")
    plt.close()


def create_metrics_heatmap(results):
    """Create heatmap of complexity metrics"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    projects = [r['project_name'] for r in results]
    
    # Normalize metrics for comparison (0-1 scale)
    metrics_data = []
    metric_names = ['SLOC\n(normalized)', 'Cyclomatic\nComplexity', 
                    'Halstead\nDifficulty', 'Halstead\nBugs']
    
    # Get raw values first
    sloc_values = [r['kloc'] * 1000 for r in results]
    # For your specific data
    cyclomatic = [1.3, 3.29, 2.86]  # From your metrics
    halstead_difficulty = [5.01, 9.74, 14.5]  # From your metrics
    halstead_bugs = [4.69, 1.96, 0.38]  # From your metrics
    
    # Normalize to 0-10 scale for better visualization
    max_sloc = max(sloc_values)
    metrics_data = [
        [v/max_sloc * 10 for v in sloc_values],
        cyclomatic,
        halstead_difficulty,
        halstead_bugs
    ]
    
    # Transpose for project-wise view
    metrics_data = np.array(metrics_data).T
    
    # Create heatmap
    im = ax.imshow(metrics_data, cmap='YlOrRd', aspect='auto', vmin=0)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(metric_names)))
    ax.set_yticks(np.arange(len(projects)))
    ax.set_xticklabels(metric_names)
    ax.set_yticklabels(projects)
    
    # Rotate the tick labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Relative Complexity', rotation=270, labelpad=20)
    
    # Add values in cells
    for i in range(len(projects)):
        for j in range(len(metric_names)):
            text = ax.text(j, i, f'{metrics_data[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)
    
    ax.set_title('Code Complexity Metrics Comparison', fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('metrics_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: metrics_heatmap.png")
    plt.close()


def create_cost_drivers_chart(results):
    """Create visualization of key cost drivers"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Key Cost Drivers Analysis', fontsize=14, fontweight='bold')
    
    # Key cost drivers to visualize
    driver_names = ['CPLX', 'PCAP', 'ACAP', 'TOOL', 'MODP']
    driver_labels = ['Complexity', 'Programmer\nCapability', 'Analyst\nCapability', 
                     'Tools', 'Modern\nPractices']
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    for idx, result in enumerate(results):
        ax = axes[idx]
        driver_values = [result['cost_drivers'][d] for d in driver_names]
        
        # Create horizontal bar chart
        y_pos = np.arange(len(driver_labels))
        bars = ax.barh(y_pos, driver_values, color=colors[idx], alpha=0.7, edgecolor='black')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(driver_labels)
        ax.set_xlabel('Cost Driver Value', fontsize=9)
        ax.set_title(result['project_name'], fontweight='bold')
        ax.set_xlim([0.6, 1.6])
        ax.axvline(x=1.0, color='red', linestyle='--', alpha=0.5, label='Nominal')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, driver_values)):
            width = bar.get_width()
            label_x_pos = width + 0.02 if width > 1.0 else width - 0.02
            ha = 'left' if width > 1.0 else 'right'
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2,
                    f'{value:.2f}',
                    ha=ha, va='center', fontsize=9, fontweight='bold')
        
        if idx == 0:
            ax.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig('cost_drivers.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: cost_drivers.png")
    plt.close()


def create_effort_breakdown(results):
    """Create pie charts showing effort distribution"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Development Effort Distribution', fontsize=14, fontweight='bold')
    
    # Typical phase distribution for organic projects
    phases = ['Requirements\n& Design', 'Implementation', 'Testing', 'Deployment']
    phase_percentages = [0.15, 0.50, 0.30, 0.05]  # Typical distribution
    colors_pie = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    for idx, result in enumerate(results):
        ax = axes[idx]
        total_effort = result['intermediate_cocomo']['effort_pm']
        
        # Calculate effort per phase
        effort_values = [total_effort * p for p in phase_percentages]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(effort_values, labels=phases, autopct='%1.1f%%',
                                            colors=colors_pie, startangle=90,
                                            explode=(0.05, 0, 0, 0))
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax.set_title(f"{result['project_name']}\n({total_effort:.2f} PM)", 
                     fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('effort_breakdown.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: effort_breakdown.png")
    plt.close()


def create_timeline_gantt(results):
    """Create Gantt-style timeline visualization"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    projects = [r['project_name'] for r in results]
    times = [r['intermediate_cocomo']['time_months'] for r in results]
    
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    # Create timeline
    y_pos = np.arange(len(projects))
    
    for i, (project, time, color) in enumerate(zip(projects, times, colors)):
        # Main bar
        ax.barh(i, time, height=0.6, color=color, alpha=0.7, edgecolor='black', linewidth=2)
        
        # Add milestone markers (simplified)
        milestones = [time * 0.2, time * 0.6, time * 0.9]  # Design, Implementation, Testing
        for milestone in milestones:
            ax.plot(milestone, i, 'D', color='black', markersize=8, zorder=5)
        
        # Add time label
        ax.text(time + 0.1, i, f'{time:.2f} months', 
                va='center', fontweight='bold', fontsize=10)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(projects)
    ax.set_xlabel('Development Time (Months)', fontsize=12, fontweight='bold')
    ax.set_title('Project Timeline Comparison', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add phase labels
    ax.text(0, -0.8, 'Design', ha='center', fontsize=9, style='italic')
    ax.text(times[0] * 0.6, -0.8, 'Implementation', ha='center', fontsize=9, style='italic')
    ax.text(times[0] * 0.9, -0.8, 'Testing', ha='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.savefig('timeline_gantt.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: timeline_gantt.png")
    plt.close()


def generate_summary_table(results):
    """Generate a formatted text table for the report"""
    print("\n" + "="*100)
    print("SUMMARY TABLE FOR REPORT")
    print("="*100)
    
    # Header
    print(f"\n{'Project':<20} {'KLOC':<8} {'Type':<12} {'Effort(PM)':<12} {'Time(Mo)':<10} "
          f"{'Team':<8} {'EAF':<8} {'Prod.':<10}")
    print("-"*100)
    
    # Data rows
    for r in results:
        inter = r['intermediate_cocomo']
        print(f"{r['project_name']:<20} {r['kloc']:<8.3f} {r['project_type']:<12} "
              f"{inter['effort_pm']:<12.2f} {inter['time_months']:<10.2f} "
              f"{inter['avg_people']:<8.2f} {inter['eaf']:<8.3f} {inter['productivity']:<10.3f}")
    
    print("\n" + "="*100 + "\n")


def main():
    """Main visualization function"""
    print("\n" + "="*80)
    print("COCOMO RESULTS VISUALIZATION")
    print("="*80 + "\n")
    
    try:
        # Load results
        print("Loading results from cocomo_results.json...")
        results = load_results()
        print(f"✓ Loaded {len(results)} projects\n")
        
        # Generate visualizations
        print("Generating visualizations...")
        print("-"*80)
        
        create_comparison_chart(results)
        create_metrics_heatmap(results)
        create_cost_drivers_chart(results)
        create_effort_breakdown(results)
        create_timeline_gantt(results)
        
        print("-"*80)
        print("\nGenerating summary table...")
        generate_summary_table(results)
        
        print("="*80)
        print("✓ All visualizations generated successfully!")
        print("="*80)
        print("\nGenerated files:")
        print("  • cocomo_comparison.png - Main comparison charts")
        print("  • metrics_heatmap.png - Complexity metrics heatmap")
        print("  • cost_drivers.png - Cost drivers analysis")
        print("  • effort_breakdown.png - Effort distribution pie charts")
        print("  • timeline_gantt.png - Project timeline comparison")
        
    except FileNotFoundError:
        print("❌ Error: cocomo_results.json not found!")
        print("Please run cocomo_analysis.py first to generate results.")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
