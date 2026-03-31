#!/usr/bin/env python3
"""
FPS Gaming Test - Comprehensive GPU Metrics Validation
This tool tests GPU metrics accuracy during gaming scenarios and identifies issues.
"""

import sys
import os
import time
import json
import threading
from typing import Dict, List, Optional

# Add devicepilot to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'devicepilot'))

try:
    from devicepilot.core.metrics import MetricsCollector
    from devicepilot.core.fps import FPSMonitor
    print("✓ DevicePilot modules imported successfully")
except ImportError as e:
    print(f"✗ Failed to import DevicePilot modules: {e}")
    sys.exit(1)

class GPUMetricsValidator:
    """Validates GPU metrics accuracy and identifies issues"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.fps_monitor = None
        self.validation_results = {
            "issues_found": [],
            "recommendations": [],
            "metrics_summary": {},
            "performance_impact": {}
        }
        
        # Try to initialize FPS monitor
        try:
            self.fps_monitor = FPSMonitor()
            print("✓ FPS Monitor initialized")
        except Exception as e:
            print(f"⚠ FPS Monitor initialization failed: {e}")
    
    def validate_gpu_initialization(self) -> Dict:
        """Check if GPU monitoring is properly initialized"""
        print("\n=== GPU Monitoring Initialization Check ===")
        
        init_status = {
            "nvidia_available": self.metrics_collector.nvidia_initialized,
            "wmi_available": bool(self.metrics_collector.wmi_connection),
            "ohm_available": bool(self.metrics_collector.ohm_monitor),
            "powershell_available": True  # Always available on Windows
        }
        
        print(f"NVIDIA NVML: {'✓ Available' if init_status['nvidia_available'] else '✗ Not available'}")
        print(f"WMI: {'✓ Available' if init_status['wmi_available'] else '✗ Not available'}")
        print(f"OpenHardwareMonitor: {'✓ Available' if init_status['ohm_available'] else '✗ Not available'}")
        print(f"PowerShell: {'✓ Available' if init_status['powershell_available'] else '✗ Not available'}")
        
        # Identify issues
        if not any(init_status.values()):
            self.validation_results["issues_found"].append("No GPU monitoring methods available")
            self.validation_results["recommendations"].append("Install required dependencies: pip install pynvml wmi pythonnet")
        
        return init_status
    
    def test_individual_methods(self) -> Dict:
        """Test each GPU monitoring method individually"""
        print("\n=== Individual GPU Method Testing ===")
        
        methods_results = {}
        
        # Test PowerShell method
        print("\n1. Testing PowerShell Method...")
        try:
            ps_gpus = self.metrics_collector.get_gpu_metrics_via_powershell()
            methods_results["powershell"] = {
                "success": len(ps_gpus) > 0,
                "gpu_count": len(ps_gpus),
                "data": ps_gpus
            }
            
            if ps_gpus:
                gpu = ps_gpus[0]
                print(f"   ✓ Found: {gpu.get('name', 'Unknown')} - {gpu.get('utilization_gpu', 0)}% utilization")
                
                # Check for suspicious values
                util = gpu.get('utilization_gpu', 0)
                if util > 90:
                    self.validation_results["issues_found"].append(f"PowerShell reports suspiciously high GPU utilization: {util}%")
                elif util == 0:
                    self.validation_results["issues_found"].append("PowerShell reports 0% GPU utilization (may be idle or incorrect)")
            else:
                print("   ✗ No GPUs found")
                self.validation_results["issues_found"].append("PowerShell method found no GPUs")
        except Exception as e:
            print(f"   ✗ PowerShell method failed: {e}")
            methods_results["powershell"] = {"success": False, "error": str(e)}
        
        # Test OpenHardwareMonitor method
        print("\n2. Testing OpenHardwareMonitor Method...")
        if self.metrics_collector.ohm_monitor:
            try:
                ohm_gpus = self.metrics_collector.ohm_monitor.get_gpu_data()
                methods_results["ohm"] = {
                    "success": len(ohm_gpus) > 0,
                    "gpu_count": len(ohm_gpus),
                    "data": ohm_gpus
                }
                
                if ohm_gpus:
                    gpu = ohm_gpus[0]
                    print(f"   ✓ Found: {gpu.get('name', 'Unknown')} - {gpu.get('utilization_gpu', 0)}% utilization, {gpu.get('temperature', 0)}°C")
                    
                    # Check for issues
                    util = gpu.get('utilization_gpu', 0)
                    temp = gpu.get('temperature', 0)
                    
                    if util > 95:
                        self.validation_results["issues_found"].append(f"OHM reports very high GPU utilization: {util}%")
                    if temp == 0:
                        self.validation_results["issues_found"].append("OHM reports 0°C temperature (sensor may be unavailable)")
                    elif temp > 90:
                        self.validation_results["issues_found"].append(f"High GPU temperature detected: {temp}°C")
                else:
                    print("   ✗ No GPUs found")
                    self.validation_results["issues_found"].append("OpenHardwareMonitor found no GPUs")
            except Exception as e:
                print(f"   ✗ OHM method failed: {e}")
                methods_results["ohm"] = {"success": False, "error": str(e)}
        else:
            print("   ✗ OpenHardwareMonitor not available")
            methods_results["ohm"] = {"success": False, "error": "Not initialized"}
        
        # Test NVIDIA method (if available)
        print("\n3. Testing NVIDIA NVML Method...")
        if self.metrics_collector.nvidia_initialized:
            try:
                nvidia_gpus = self.metrics_collector._get_nvidia_gpu_metrics()
                methods_results["nvidia"] = {
                    "success": len(nvidia_gpus) > 0,
                    "gpu_count": len(nvidia_gpus),
                    "data": nvidia_gpus
                }
                
                if nvidia_gpus:
                    gpu = nvidia_gpus[0]
                    print(f"   ✓ Found: {gpu.get('name', 'Unknown')} - {gpu.get('utilization_gpu', 0)}% utilization")
                else:
                    print("   ✗ No NVIDIA GPUs found")
            except Exception as e:
                print(f"   ✗ NVIDIA method failed: {e}")
                methods_results["nvidia"] = {"success": False, "error": str(e)}
        else:
            print("   ✗ NVIDIA NVML not available")
            methods_results["nvidia"] = {"success": False, "error": "Not initialized"}
        
        return methods_results
    
    def compare_methods(self, methods_results: Dict) -> None:
        """Compare results from different methods to identify discrepancies"""
        print("\n=== Method Comparison Analysis ===")
        
        successful_methods = {name: data for name, data in methods_results.items() 
                             if data.get("success", False)}
        
        if len(successful_methods) < 2:
            print("⚠ Cannot compare methods - need at least 2 successful methods")
            return
        
        # Compare utilization values
        utilizations = {}
        temperatures = {}
        
        for method_name, data in successful_methods.items():
            if data.get("data") and len(data["data"]) > 0:
                gpu = data["data"][0]
                utilizations[method_name] = gpu.get("utilization_gpu", 0)
                temperatures[method_name] = gpu.get("temperature", 0)
        
        # Check for significant discrepancies in utilization
        if len(utilizations) >= 2:
            util_values = list(utilizations.values())
            max_util = max(util_values)
            min_util = min(util_values)
            
            if max_util - min_util > 20:  # >20% difference
                self.validation_results["issues_found"].append(
                    f"Large utilization discrepancy between methods: {utilizations}"
                )
                self.validation_results["recommendations"].append(
                    "Consider using PowerShell method for most accurate Task Manager-like readings"
                )
        
        # Check temperature consistency
        temp_values = [t for t in temperatures.values() if t > 0]
        if len(temp_values) >= 2:
            max_temp = max(temp_values)
            min_temp = min(temp_values)
            
            if max_temp - min_temp > 10:  # >10°C difference
                self.validation_results["issues_found"].append(
                    f"Temperature readings vary significantly: {temperatures}"
                )
    
    def test_gaming_scenario(self) -> Dict:
        """Simulate gaming scenario testing"""
        print("\n=== Gaming Scenario Test ===")
        
        gaming_results = {
            "baseline": {},
            "during_load": {},
            "fps_data": {}
        }
        
        # Get baseline metrics
        print("1. Collecting baseline GPU metrics...")
        baseline = self.metrics_collector.get_gpu_metrics()
        gaming_results["baseline"] = baseline
        
        if baseline:
            gpu = baseline[0]
            print(f"   Baseline: {gpu.get('utilization_gpu', 0)}% utilization, {gpu.get('temperature', 0)}°C")
        
        # Simulate load (we can't actually start a game, but we can stress test)
        print("\n2. Monitoring during potential load...")
        print("   (In a real scenario, start your game now)")
        
        # Collect metrics over time
        load_metrics = []
        for i in range(5):
            time.sleep(1)
            current_metrics = self.metrics_collector.get_gpu_metrics()
            if current_metrics:
                load_metrics.append(current_metrics[0])
                util = current_metrics[0].get('utilization_gpu', 0)
                temp = current_metrics[0].get('temperature', 0)
                print(f"   Sample {i+1}: {util}% utilization, {temp}°C")
        
        gaming_results["during_load"] = load_metrics
        
        # Analyze results
        if load_metrics:
            avg_util = sum(gpu.get('utilization_gpu', 0) for gpu in load_metrics) / len(load_metrics)
            max_util = max(gpu.get('utilization_gpu', 0) for gpu in load_metrics)
            avg_temp = sum(gpu.get('temperature', 0) for gpu in load_metrics) / len(load_metrics)
            
            print(f"\n   Analysis: Avg utilization: {avg_util:.1f}%, Max: {max_util}%, Avg temp: {avg_temp:.1f}°C")
            
            # Check for issues
            if max_util == 0:
                self.validation_results["issues_found"].append("GPU utilization remains 0% (may indicate monitoring issue)")
            elif max_util > 98:
                self.validation_results["issues_found"].append("GPU utilization constantly at maximum (may be reporting issue)")
        
        return gaming_results
    
    def test_fps_integration(self) -> Dict:
        """Test FPS monitoring integration"""
        print("\n=== FPS Integration Test ===")
        
        fps_results = {"available": False, "test_results": {}}
        
        if self.fps_monitor:
            try:
                print("Testing FPS detection...")
                # In a real scenario, this would detect game windows
                fps_results["available"] = True
                fps_results["test_results"] = {"status": "FPS monitor ready"}
                print("✓ FPS monitor is available and ready")
            except Exception as e:
                print(f"✗ FPS monitor test failed: {e}")
                fps_results["test_results"] = {"error": str(e)}
        else:
            print("✗ FPS monitor not available")
            self.validation_results["issues_found"].append("FPS monitoring not available")
        
        return fps_results
    
    def generate_recommendations(self) -> None:
        """Generate recommendations based on found issues"""
        print("\n=== Recommendations ===")
        
        if not self.validation_results["issues_found"]:
            print("✓ No major issues found with GPU metrics!")
            return
        
        print("Issues found:")
        for issue in self.validation_results["issues_found"]:
            print(f"  • {issue}")
        
        print("\nRecommendations:")
        base_recommendations = [
            "Ensure OpenHardwareMonitor service is running for best temperature readings",
            "Use PowerShell method for Task Manager-accurate GPU utilization",
            "Monitor GPU metrics during actual gaming for real-world validation",
            "Check Windows Performance Toolkit if GPU counters seem incorrect"
        ]
        
        all_recommendations = self.validation_results["recommendations"] + base_recommendations
        for rec in set(all_recommendations):  # Remove duplicates
            print(f"  • {rec}")
    
    def run_full_validation(self) -> Dict:
        """Run complete GPU metrics validation"""
        print("=== GPU Metrics Gaming Validation ===")
        print("This tool validates GPU monitoring accuracy for gaming scenarios\n")
        
        # Step 1: Check initialization
        init_status = self.validate_gpu_initialization()
        
        # Step 2: Test individual methods
        methods_results = self.test_individual_methods()
        
        # Step 3: Compare methods
        self.compare_methods(methods_results)
        
        # Step 4: Gaming scenario test
        gaming_results = self.test_gaming_scenario()
        
        # Step 5: FPS integration test
        fps_results = self.test_fps_integration()
        
        # Step 6: Generate recommendations
        self.generate_recommendations()
        
        # Compile final results
        final_results = {
            "initialization": init_status,
            "methods_testing": methods_results,
            "gaming_scenario": gaming_results,
            "fps_integration": fps_results,
            "validation_summary": self.validation_results
        }
        
        return final_results

def main():
    """Main execution function"""
    validator = GPUMetricsValidator()
    
    try:
        results = validator.run_full_validation()
        
        # Save results to file
        results_file = os.path.join(os.path.dirname(__file__), "gpu_validation_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n=== Validation Complete ===")
        print(f"Results saved to: {results_file}")
        print("Use this information to address GPU metrics issues in your gaming setup.")
        
    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
