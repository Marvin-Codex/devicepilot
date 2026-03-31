#!/usr/bin/env python3
"""
GPU Debug Tool to test GPU metrics collection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'devicepilot'))

from devicepilot.core.metrics import MetricsCollector
import json

def main():
    print("=== GPU Metrics Debug Tool ===")
    print()
    
    # Initialize metrics collector
    metrics = MetricsCollector()
    
    print("Available GPU monitoring methods:")
    print(f"- NVIDIA NVML: {'Available' if metrics.nvidia_initialized else 'Not available'}")
    print(f"- WMI: {'Available' if metrics.wmi_connection else 'Not available'}")
    print(f"- OpenHardwareMonitor: {'Available' if metrics.ohm_monitor else 'Not available'}")
    print()
    
    # Get GPU metrics
    print("=== Collecting GPU metrics ===")
    gpu_data = metrics.get_gpu_metrics()
    
    print(f"Found {len(gpu_data)} GPU(s):")
    for i, gpu in enumerate(gpu_data):
        print(f"\nGPU {i}:")
        print(f"  Name: {gpu.get('name', 'Unknown')}")
        print(f"  Vendor: {gpu.get('vendor', 'Unknown')}")
        print(f"  GPU Utilization: {gpu.get('utilization_gpu', 0)}%")
        print(f"  Memory Utilization: {gpu.get('utilization_memory', 0)}%")
        print(f"  Temperature: {gpu.get('temperature', 0)}°C")
        print(f"  Memory Used: {gpu.get('memory_used_mb', 0):.1f} MB")
        print(f"  Memory Total: {gpu.get('memory_total_mb', 0):.1f} MB")
        print(f"  Power: {gpu.get('power_watts', 0)} W")
        print(f"  Clock Graphics: {gpu.get('clock_graphics_mhz', 0)} MHz")
        print(f"  Clock Memory: {gpu.get('clock_memory_mhz', 0)} MHz")
    
    if not gpu_data:
        print("No GPUs found or no data available")
    
    print("\n=== Raw GPU Data ===")
    print(json.dumps(gpu_data, indent=2))
    
    # Test OpenHardwareMonitor specifically
    if metrics.ohm_monitor:
        print("\n=== OpenHardwareMonitor GPU Data ===")
        ohm_gpu_data = metrics.ohm_monitor.get_gpu_data()
        print(json.dumps(ohm_gpu_data, indent=2))
        
        print("\n=== All OHM Sensors ===")
        all_sensors = metrics.ohm_monitor.get_all_sensors()
        loads = all_sensors.get("loads", {})
        for hardware_name, sensors in loads.items():
            if any(keyword in hardware_name.lower() for keyword in ["gpu", "graphics", "video", "nvidia", "amd", "radeon", "geforce"]):
                print(f"\nGPU Load Sensors for {hardware_name}:")
                for sensor in sensors:
                    print(f"  {sensor['name']}: {sensor['value']}{sensor['unit']}")

if __name__ == "__main__":
    main()
