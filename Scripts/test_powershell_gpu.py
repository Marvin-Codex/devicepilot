#!/usr/bin/env python3
"""
Test PowerShell GPU method directly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'devicepilot'))

from devicepilot.core.metrics import MetricsCollector
import json

def main():
    print("=== PowerShell GPU Method Test ===")
    
    metrics = MetricsCollector()
    
    print("Testing PowerShell method directly...")
    ps_gpus = metrics.get_gpu_metrics_via_powershell()
    
    print(f"PowerShell found {len(ps_gpus)} GPU(s):")
    for gpu in ps_gpus:
        print(f"  {gpu.get('name', 'Unknown')}: {gpu.get('utilization_gpu', 0)}%")
    
    print("\nFull PowerShell GPU data:")
    print(json.dumps(ps_gpus, indent=2))
    
    print("\n=== Now testing main GPU method ===")
    gpu_data = metrics.get_gpu_metrics()
    
    print(f"Main method found {len(gpu_data)} GPU(s):")
    for gpu in gpu_data:
        source = gpu.get('source', 'unknown')
        print(f"  {gpu.get('name', 'Unknown')}: {gpu.get('utilization_gpu', 0)}% (source: {source})")

if __name__ == "__main__":
    main()
