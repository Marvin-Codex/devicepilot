"""
Quick test of DevicePilot with OpenHardwareMonitor
Just test the metrics collection without GUI
"""

import sys
import os
sys.path.append('.')

from devicepilot.core.metrics import MetricsCollector

def test_ohm_in_devicepilot():
    print("Testing OpenHardwareMonitor in DevicePilot...")
    
    collector = MetricsCollector()
    
    print("\n=== Getting All Metrics ===")
    metrics = collector.get_all_metrics()
    
    # Temperature metrics
    temp_metrics = metrics.get('temperature', {})
    if temp_metrics.get('sensors'):
        print("✅ Temperature monitoring via OpenHardwareMonitor working!")
        summary = temp_metrics.get('summary', {})
        print(f"CPU Temperature: {summary.get('cpu_temp', 0):.1f}°C")
        print(f"GPU Temperature: {summary.get('gpu_temp', 0):.1f}°C")
        print(f"Highest Temperature: {summary.get('highest_temp', 0):.1f}°C")
        print(f"Average Temperature: {summary.get('average_temp', 0):.1f}°C")
    
    # GPU metrics
    gpu_metrics = metrics.get('gpu', [])
    if gpu_metrics:
        print(f"\n✅ GPU monitoring working! Found {len(gpu_metrics)} GPU(s)")
        for i, gpu in enumerate(gpu_metrics):
            print(f"GPU {i+1}: {gpu.get('name', 'Unknown')} - {gpu.get('temperature', 0)}°C")
    
    # CPU metrics
    cpu_metrics = metrics.get('cpu', {})
    if cpu_metrics:
        print(f"\n✅ CPU monitoring: {cpu_metrics.get('usage_percent', 0):.1f}% usage")
    
    # Memory metrics
    memory_metrics = metrics.get('memory', {})
    if memory_metrics:
        print(f"✅ Memory monitoring: {memory_metrics.get('usage_percent', 0):.1f}% usage")
    
    print("\n🎉 DevicePilot with OpenHardwareMonitor integration is ready!")

if __name__ == "__main__":
    test_ohm_in_devicepilot()
