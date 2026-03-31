"""
Test GPU utilization detection and display
Check if GPU load data is properly coming through
"""

import sys
import os
sys.path.append('.')

from devicepilot.core.ohm_monitor import get_hardware_monitor
from devicepilot.core.metrics import MetricsCollector

def test_gpu_utilization():
    """Test GPU utilization detection"""
    print("=== GPU Utilization Test ===")
    
    # Test direct OpenHardwareMonitor
    print("\n1. Testing OpenHardwareMonitor directly...")
    monitor = get_hardware_monitor()
    if monitor:
        all_data = monitor.get_all_sensors()
        loads = all_data.get("loads", {})
        
        print("GPU Load sensors found:")
        for hardware_name, sensors in loads.items():
            if any(keyword in hardware_name.lower() for keyword in ["gpu", "graphics", "amd", "nvidia", "radeon"]):
                print(f"  Hardware: {hardware_name}")
                for sensor in sensors:
                    sensor_name = sensor.get("name", "Unknown")
                    sensor_value = sensor.get("value", 0)
                    print(f"    • {sensor_name}: {sensor_value:.1f}%")
        
        # Test GPU data method
        gpu_data = monitor.get_gpu_data()
        print(f"\nGPU data from get_gpu_data(): {len(gpu_data)} GPUs")
        for i, gpu in enumerate(gpu_data):
            print(f"  GPU {i+1}:")
            print(f"    Name: {gpu.get('name', 'Unknown')}")
            print(f"    Load: {gpu.get('utilization_gpu', 0)}%")
            print(f"    Temperature: {gpu.get('temperature', 0)}°C")
    
    # Test MetricsCollector
    print("\n2. Testing MetricsCollector integration...")
    collector = MetricsCollector()
    all_metrics = collector.get_all_metrics()
    
    gpu_metrics = all_metrics.get("gpu", [])
    print(f"GPU metrics from collector: {len(gpu_metrics)} GPUs")
    
    for i, gpu in enumerate(gpu_metrics):
        print(f"  GPU {i+1}:")
        print(f"    Name: {gpu.get('name', 'Unknown')}")
        print(f"    Vendor: {gpu.get('vendor', 'Unknown')}")
        print(f"    Utilization GPU: {gpu.get('utilization_gpu', 0)}%")
        print(f"    Utilization Memory: {gpu.get('utilization_memory', 0)}%")
        print(f"    Temperature: {gpu.get('temperature', 0)}°C")
        print(f"    Memory Total: {gpu.get('memory_total_mb', 0):.1f}MB")
    
    # Test what the overlay would see
    print("\n3. Overlay integration test...")
    if gpu_metrics:
        primary_gpu = gpu_metrics[0]
        gpu_util = primary_gpu.get("utilization_gpu", 0)
        print(f"Primary GPU utilization for overlay: {gpu_util}%")
        
        if gpu_util == 0:
            print("⚠️  GPU utilization is 0% - this might be normal if GPU is idle")
            print("   Try running a GPU-intensive application and check again")
        else:
            print("✅ GPU utilization detected successfully!")
    else:
        print("❌ No GPU metrics available for overlay")

if __name__ == "__main__":
    test_gpu_utilization()
