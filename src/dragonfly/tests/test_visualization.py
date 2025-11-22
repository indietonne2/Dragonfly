"""
Author: Test Automation Team
Version: 1.0.0
Description: Visualization script for Dragonfly NBR test results
Filename: test_visualization.py
Pathname: /tests/test_visualization.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from pathlib import Path


class NBRVisualizer:
    """Creates publication-quality visualizations of NBR test results"""
    
    # USGS Burn Severity Color Scheme
    SEVERITY_COLORS = ['#0000FF', '#7FFF00', '#FFFF00', '#FFA500', '#FF4500', '#8B0000']
    SEVERITY_LABELS = ['Enhanced Regrowth', 'Unburned', 'Low Severity', 
                       'Moderate-Low', 'Moderate-High', 'High Severity']
    
    def __init__(self, dpi: int = 150):
        self.dpi = dpi
        plt.style.use('default')
    
    def create_four_panel_plot(self, nbr_pre, nbr_post, dnbr, severity, output_path, title="NBR Analysis"):
        """Create 4-panel visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Panel 1: NBR Pre-fire
        im1 = axes[0, 0].imshow(nbr_pre, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[0, 0].set_title('Pre-Fire NBR', fontweight='bold')
        axes[0, 0].axis('off')
        plt.colorbar(im1, ax=axes[0, 0], fraction=0.046, pad=0.04, label='NBR Value')
        
        # Panel 2: NBR Post-fire
        im2 = axes[0, 1].imshow(nbr_post, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[0, 1].set_title('Post-Fire NBR', fontweight='bold')
        axes[0, 1].axis('off')
        plt.colorbar(im2, ax=axes[0, 1], fraction=0.046, pad=0.04, label='NBR Value')
        
        # Panel 3: dNBR
        im3 = axes[1, 0].imshow(dnbr, cmap='hot', vmin=-0.5, vmax=1.0)
        axes[1, 0].set_title('Delta NBR (dNBR)', fontweight='bold')
        axes[1, 0].axis('off')
        plt.colorbar(im3, ax=axes[1, 0], fraction=0.046, pad=0.04, label='dNBR Value')
        
        # Panel 4: Severity
        cmap = ListedColormap(self.SEVERITY_COLORS)
        norm = BoundaryNorm(range(7), cmap.N)
        im4 = axes[1, 1].imshow(severity, cmap=cmap, norm=norm)
        axes[1, 1].set_title('USGS Burn Severity Classification', fontweight='bold')
        axes[1, 1].axis('off')
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=self.SEVERITY_COLORS[i], label=self.SEVERITY_LABELS[i])
                          for i in range(6)]
        axes[1, 1].legend(handles=legend_elements, loc='center left', 
                         bbox_to_anchor=(1.05, 0.5), frameon=True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved 4-panel plot: {output_path}")
        plt.close()
    
    def create_histogram_comparison(self, nbr_pre, nbr_post, dnbr, output_path):
        """Create histogram comparison"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        fig.suptitle('NBR Distribution Analysis', fontsize=14, fontweight='bold')
        
        # Pre-fire
        axes[0].hist(nbr_pre.flatten(), bins=50, color='green', alpha=0.7, edgecolor='black')
        axes[0].axvline(x=nbr_pre.mean(), color='red', linestyle='--', linewidth=2)
        axes[0].set_xlabel('NBR Value')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Pre-Fire NBR Distribution')
        axes[0].grid(True, alpha=0.3)
        
        # Post-fire
        axes[1].hist(nbr_post.flatten(), bins=50, color='orange', alpha=0.7, edgecolor='black')
        axes[1].axvline(x=nbr_post.mean(), color='red', linestyle='--', linewidth=2)
        axes[1].set_xlabel('NBR Value')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Post-Fire NBR Distribution')
        axes[1].grid(True, alpha=0.3)
        
        # dNBR
        axes[2].hist(dnbr.flatten(), bins=50, color='red', alpha=0.7, edgecolor='black')
        axes[2].axvline(x=0.10, color='yellow', linestyle='--', linewidth=2, label='Low (0.10)')
        axes[2].axvline(x=0.27, color='orange', linestyle='--', linewidth=2, label='Mod-Low (0.27)')
        axes[2].axvline(x=0.66, color='darkred', linestyle='--', linewidth=2, label='High (0.66)')
        axes[2].set_xlabel('dNBR Value')
        axes[2].set_ylabel('Frequency')
        axes[2].set_title('dNBR Distribution')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved histogram plot: {output_path}")
        plt.close()
    
    def create_severity_bar_chart(self, severity, output_path):
        """Create bar chart of severity distribution"""
        counts = [np.sum(severity == i) for i in range(6)]
        total = severity.size
        percentages = [(c / total) * 100 for c in counts]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Burn Severity Distribution', fontsize=14, fontweight='bold')
        
        # Absolute counts
        bars1 = ax1.bar(range(6), counts, color=self.SEVERITY_COLORS, edgecolor='black', linewidth=1.5)
        ax1.set_xlabel('Severity Class', fontweight='bold')
        ax1.set_ylabel('Pixel Count', fontweight='bold')
        ax1.set_title('Absolute Distribution')
        ax1.set_xticks(range(6))
        ax1.set_xticklabels(self.SEVERITY_LABELS, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom', fontweight='bold')
        
        # Percentages
        bars2 = ax2.bar(range(6), percentages, color=self.SEVERITY_COLORS, edgecolor='black', linewidth=1.5)
        ax2.set_xlabel('Severity Class', fontweight='bold')
        ax2.set_ylabel('Percentage (%)', fontweight='bold')
        ax2.set_title('Relative Distribution')
        ax2.set_xticks(range(6))
        ax2.set_xticklabels(self.SEVERITY_LABELS, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved severity distribution: {output_path}")
        plt.close()
    
    def create_comparison_plot(self, nbr_pre, nbr_post, output_path):
        """Create side-by-side comparison"""
        difference = nbr_pre - nbr_post
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        fig.suptitle('NBR Temporal Comparison', fontsize=14, fontweight='bold')
        
        im1 = axes[0].imshow(nbr_pre, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[0].set_title('Pre-Fire NBR', fontweight='bold')
        axes[0].axis('off')
        plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
        
        im2 = axes[1].imshow(nbr_post, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[1].set_title('Post-Fire NBR', fontweight='bold')
        axes[1].axis('off')
        plt.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)
        
        im3 = axes[2].imshow(difference, cmap='seismic', vmin=-1, vmax=1)
        axes[2].set_title('Change Detection (dNBR)', fontweight='bold')
        axes[2].axis('off')
        plt.colorbar(im3, ax=axes[2], fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        print(f"✓ Saved comparison plot: {output_path}")
        plt.close()


def visualize_test_results(test_dir: Path = Path("test_outputs")):
    """Main visualization function"""
    print("\n" + "="*60)
    print("NBR TEST RESULTS VISUALIZATION")
    print("="*60)
    
    # Load data
    print("\n[1/5] Loading test data...")
    try:
        nbr_pre = np.load(test_dir / "mock_nbr_pre.npy")
        nbr_post = np.load(test_dir / "mock_nbr_post.npy")
        dnbr = np.load(test_dir / "mock_dnbr.npy")
        severity = np.load(test_dir / "mock_severity.npy")
    except FileNotFoundError:
        print(f"❌ Error: Test output files not found.")
        print(f"   Please run test_visual_scenario.py first.")
        return
    
    visualizer = NBRVisualizer(dpi=200)
    plots_dir = test_dir / "plots"
    plots_dir.mkdir(exist_ok=True)
    
    print("[2/5] Creating 4-panel analysis plot...")
    visualizer.create_four_panel_plot(nbr_pre, nbr_post, dnbr, severity,
                                     plots_dir / "01_four_panel_analysis.png",
                                     title="Dragonfly NBR Toolkit - Test Results")
    
    print("[3/5] Creating histogram comparison...")
    visualizer.create_histogram_comparison(nbr_pre, nbr_post, dnbr,
                                          plots_dir / "02_histogram_comparison.png")
    
    print("[4/5] Creating severity distribution chart...")
    visualizer.create_severity_bar_chart(severity, plots_dir / "03_severity_distribution.png")
    
    print("[5/5] Creating temporal comparison...")
    visualizer.create_comparison_plot(nbr_pre, nbr_post, plots_dir / "04_temporal_comparison.png")
    
    print("\n" + "="*60)
    print("✅ VISUALIZATION COMPLETE")
    print("="*60)
    print(f"\nGenerated plots in: {plots_dir}")
    print("\n" + "="*60)


if __name__ == "__main__":
    visualize_test_results()
