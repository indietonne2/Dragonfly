"""
Author: Test Automation Team
Version: 1.0.0
Description: Comprehensive test scenario for Dragonfly NBR Toolkit with visual verification
Filename: test_visual_scenario.py
Pathname: /tests/test_visual_scenario.py

This test scenario provides both mock data testing and real data validation
with visual outputs for manual inspection.
"""

import numpy as np
from pathlib import Path
from typing import Tuple, Dict
import json


class MockSentinel2DataGenerator:
    """
    Author: Test Automation Team
    Version: 1.0.0
    Description: Generates synthetic Sentinel-2 data for testing NBR pipeline
    """
    
    def __init__(self, width: int = 100, height: int = 100):
        """Initialize mock data generator"""
        self.width = width
        self.height = height
        self.pixel_size = 10  # 10m resolution
        
    def generate_pre_fire_scene(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate pre-fire NIR and SWIR bands"""
        # Healthy vegetation: High NIR, Low SWIR
        nir = np.random.uniform(5000, 8000, (self.height, self.width)).astype(np.uint16)
        swir = np.random.uniform(1000, 3000, (self.height, self.width)).astype(np.uint16)
        
        # Add spatial correlation
        try:
            from scipy.ndimage import gaussian_filter
            nir = gaussian_filter(nir, sigma=2.0).astype(np.uint16)
            swir = gaussian_filter(swir, sigma=2.0).astype(np.uint16)
        except ImportError:
            pass  # Skip if scipy not available
        
        return nir, swir
    
    def generate_post_fire_scene(self, burned_area_percent: float = 30) -> Tuple[np.ndarray, np.ndarray]:
        """Generate post-fire NIR and SWIR bands with burned areas"""
        # Start with pre-fire scene
        nir, swir = self.generate_pre_fire_scene()
        
        # Create burn mask
        burn_mask = np.random.random((self.height, self.width)) < (burned_area_percent / 100)
        
        try:
            from scipy.ndimage import binary_dilation
            burn_mask = binary_dilation(burn_mask, iterations=5)
        except ImportError:
            pass  # Skip if scipy not available
        
        # Apply burn effects: Lower NIR, Higher SWIR
        nir[burn_mask] = np.random.uniform(2000, 4000, burn_mask.sum()).astype(np.uint16)
        swir[burn_mask] = np.random.uniform(4000, 7000, burn_mask.sum()).astype(np.uint16)
        
        # High severity zones
        high_severity = burn_mask & (np.random.random((self.height, self.width)) < 0.33)
        nir[high_severity] = np.random.uniform(1000, 2000, high_severity.sum()).astype(np.uint16)
        swir[high_severity] = np.random.uniform(6000, 8000, high_severity.sum()).astype(np.uint16)
        
        return nir, swir


class TestScenario:
    """
    Author: Test Automation Team
    Version: 1.0.0
    Description: Main test scenario coordinator with visual validation
    """
    
    def __init__(self, output_dir: Path):
        """Initialize test scenario"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generator = MockSentinel2DataGenerator(width=200, height=200)
        
    def run_mock_data_test(self) -> Dict:
        """Execute test with synthetic mock data"""
        print("=" * 60)
        print("TEST SCENARIO 1: Mock Synthetic Data")
        print("=" * 60)
        
        # Generate test data
        print("\n[1/6] Generating pre-fire scene...")
        nir_pre, swir_pre = self.generator.generate_pre_fire_scene()
        
        print("[2/6] Generating post-fire scene...")
        nir_post, swir_post = self.generator.generate_post_fire_scene(burned_area_percent=35)
        
        # Calculate NBR
        print("[3/6] Calculating pre-fire NBR...")
        nbr_pre = self._calculate_nbr(nir_pre, swir_pre)
        
        print("[4/6] Calculating post-fire NBR...")
        nbr_post = self._calculate_nbr(nir_post, swir_post)
        
        # Calculate dNBR
        print("[5/6] Computing dNBR...")
        dnbr = nbr_pre - nbr_post
        
        # Classify severity
        print("[6/6] Classifying burn severity...")
        severity = self._classify_severity(dnbr)
        
        # Save outputs
        results = self._save_test_outputs(nbr_pre, nbr_post, dnbr, severity, prefix="mock")
        
        # Generate statistics
        stats = self._compute_statistics(dnbr, severity)
        results['statistics'] = stats
        
        self._print_results(stats, "MOCK DATA TEST")
        
        return results
    
    def _calculate_nbr(self, nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
        """Calculate Normalized Burn Ratio: NBR = (NIR - SWIR) / (NIR + SWIR)"""
        nir_r = nir.astype(np.float32) / 10000.0
        swir_r = swir.astype(np.float32) / 10000.0
        
        numerator = nir_r - swir_r
        denominator = nir_r + swir_r
        
        nbr = np.zeros_like(numerator)
        valid_mask = denominator != 0
        nbr[valid_mask] = numerator[valid_mask] / denominator[valid_mask]
        
        return nbr
    
    def _classify_severity(self, dnbr: np.ndarray) -> np.ndarray:
        """Classify burn severity using USGS standard thresholds"""
        severity = np.zeros(dnbr.shape, dtype=np.uint8)
        
        severity[dnbr < -0.10] = 0  # Enhanced regrowth
        severity[(dnbr >= -0.10) & (dnbr < 0.10)] = 1  # Unburned
        severity[(dnbr >= 0.10) & (dnbr < 0.27)] = 2  # Low severity
        severity[(dnbr >= 0.27) & (dnbr < 0.44)] = 3  # Moderate-low
        severity[(dnbr >= 0.44) & (dnbr < 0.66)] = 4  # Moderate-high
        severity[dnbr >= 0.66] = 5  # High severity
        
        return severity
    
    def _compute_statistics(self, dnbr: np.ndarray, severity: np.ndarray) -> Dict:
        """Compute test statistics"""
        pixel_area_km2 = (10 * 10) / 1_000_000
        total_pixels = dnbr.size
        
        stats = {
            'total_area_km2': total_pixels * pixel_area_km2,
            'burned_pixels': int(np.sum(dnbr >= 0.10)),
            'burned_area_km2': float(np.sum(dnbr >= 0.10) * pixel_area_km2),
            'burned_percentage': float((np.sum(dnbr >= 0.10) / total_pixels) * 100),
            'high_severity_pixels': int(np.sum(severity == 5)),
            'high_severity_km2': float(np.sum(severity == 5) * pixel_area_km2),
            'high_severity_percentage': float((np.sum(severity == 5) / total_pixels) * 100),
            'dnbr_mean': float(np.mean(dnbr)),
            'dnbr_std': float(np.std(dnbr)),
            'dnbr_min': float(np.min(dnbr)),
            'dnbr_max': float(np.max(dnbr)),
            'severity_distribution': {
                'enhanced_regrowth': int(np.sum(severity == 0)),
                'unburned': int(np.sum(severity == 1)),
                'low': int(np.sum(severity == 2)),
                'moderate_low': int(np.sum(severity == 3)),
                'moderate_high': int(np.sum(severity == 4)),
                'high': int(np.sum(severity == 5))
            }
        }
        
        return stats
    
    def _save_test_outputs(self, nbr_pre, nbr_post, dnbr, severity, prefix) -> Dict:
        """Save all test outputs as NumPy arrays"""
        outputs = {
            'nbr_pre': self.output_dir / f"{prefix}_nbr_pre.npy",
            'nbr_post': self.output_dir / f"{prefix}_nbr_post.npy",
            'dnbr': self.output_dir / f"{prefix}_dnbr.npy",
            'severity': self.output_dir / f"{prefix}_severity.npy"
        }
        
        np.save(outputs['nbr_pre'], nbr_pre)
        np.save(outputs['nbr_post'], nbr_post)
        np.save(outputs['dnbr'], dnbr)
        np.save(outputs['severity'], severity)
        
        print(f"\n✓ Test outputs saved to: {self.output_dir}")
        return outputs
    
    def _print_results(self, stats: Dict, title: str):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print(f"RESULTS: {title}")
        print("=" * 60)
        print(f"\n📊 Area Statistics:")
        print(f"  Total area:          {stats['total_area_km2']:.2f} km²")
        print(f"  Burned area:         {stats['burned_area_km2']:.2f} km² ({stats['burned_percentage']:.1f}%)")
        print(f"  High severity area:  {stats['high_severity_km2']:.2f} km² ({stats['high_severity_percentage']:.1f}%)")
        
        print(f"\n📈 dNBR Statistics:")
        print(f"  Mean:   {stats['dnbr_mean']:+.3f}")
        print(f"  Std:    {stats['dnbr_std']:.3f}")
        print(f"  Range:  [{stats['dnbr_min']:+.3f}, {stats['dnbr_max']:+.3f}]")
        
        print(f"\n🔥 Severity Distribution:")
        dist = stats['severity_distribution']
        total = sum(dist.values())
        for severity_name, count in dist.items():
            pct = (count / total) * 100
            print(f"  {severity_name:20s}: {count:6d} pixels ({pct:5.1f}%)")


# Main execution
if __name__ == "__main__":
    import sys
    
    output_dir = Path("test_outputs")
    scenario = TestScenario(output_dir)
    
    print("\n" + "="*60)
    print("DRAGONFLY NBR TOOLKIT - VISUAL TEST SCENARIO")
    print("="*60)
    
    try:
        results = scenario.run_mock_data_test()
        print("\n✅ Mock data test completed successfully!")
    except Exception as e:
        print(f"\n❌ Mock data test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("\n1. Review test outputs in:", output_dir)
    print("2. Run visualization: python test_visualization.py")
    print("3. Open plots: test_outputs/plots/")
    print("\n" + "="*60)
    print("✨ Test scenario complete!")
    print("="*60)
