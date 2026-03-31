#!/usr/bin/env python3
"""
Comprehensive GPU monitoring comparison test
Tests all available methods and compares results
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'devicepilot'))

from devicepilot.core.metrics import MetricsCollector
import subprocess
import json

def get_task_manager_like_gpu():
    """Get GPU utilization using the same method as Task Manager"""
    try:
        ps_command = '''
        $counters = @()
        try {
            $gpuCounters = Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -ErrorAction SilentlyContinue
            foreach ($sample in $gpuCounters.CounterSamples) {
                if ($sample.CookedValue -gt 0) {
                    $counters += [PSCustomObject]@{
                        Path = $sample.Path
                        Value = [math]::Round($sample.CookedValue, 2)
                        Instance = $sample.InstanceName
                    }
                }
            }
        } catch {}
        
        $counters | ConvertTo-Json
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]
                
                print("PowerShell GPU Engine Counters:")
                max_util = 0
                for item in data:
                    value = item.get('Value', 0)
                    instance = item.get('Instance', 'Unknown')
                    print(f"  {instance}: {value}%")
                    max_util = max(max_util, value)
                
                return max_util
            except json.JSONDecodeError:
                print("Failed to parse PowerShell output")
        
    except Exception as e:
        print(f"PowerShell method failed: {e}")
    
    return 0

def main():
    print("=== Comprehensive GPU Monitoring Test ===")
    print("Comparing different GPU monitoring methods...")
    print()
    
    # Initialize metrics collector
    metrics = MetricsCollector()
    
    print("=== Method 1: OpenHardwareMonitor (Current Method) ===")
    gpu_data = metrics.get_gpu_metrics()
    if gpu_data:
        for i, gpu in enumerate(gpu_data):
            util = gpu.get('utilization_gpu', 0)
            temp = gpu.get('temperature', 0)
            name = gpu.get('name', 'Unknown')
            print(f"GPU {i} ({name}): {util}% utilization, {temp}°C")
    else:
        print("No GPU data from current method")
    
    print("\n=== Method 2: PowerShell GPU Engine Counters (Task Manager Method) ===")
    task_manager_util = get_task_manager_like_gpu()
    
    print(f"\nMax utilization from Task Manager method: {task_manager_util}%")
    
    if gpu_data:
        current_util = gpu_data[0].get('utilization_gpu', 0)
        print(f"Current method utilization: {current_util}%")
        print(f"Difference: {abs(task_manager_util - current_util)}%")
        
        if abs(task_manager_util - current_util) > 5:
            print("⚠️  Significant difference detected!")
            print("Recommendations:")
            print("1. Use PowerShell method as backup")
            print("2. Check OpenHardwareMonitor sensor mapping")
            print("3. Verify GPU load sensor selection")
    
    print("\n=== Method 3: Direct OpenHardwareMonitor Sensor Check ===")
    if metrics.ohm_monitor:
        all_sensors = metrics.ohm_monitor.get_all_sensors()
        loads = all_sensors.get("loads", {})
        
        for hardware_name, sensors in loads.items():
            if any(keyword in hardware_name.lower() for keyword in ["gpu", "graphics", "video", "radeon"]):
                print(f"\n{hardware_name} Load Sensors:")
                for sensor in sensors:
                    sensor_name = sensor['name']
                    value = sensor['value']
                    unit = sensor.get('unit', '')
                    print(f"  {sensor_name}: {value}{unit}")

if __name__ == "__main__":
    main()
