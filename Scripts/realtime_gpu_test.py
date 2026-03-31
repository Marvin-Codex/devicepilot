#!/usr/bin/env python3
"""
Real-time GPU monitoring test to see live GPU usage
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'devicepilot'))

from devicepilot.core.metrics import MetricsCollector

def main():
    print("=== Real-time GPU Monitoring Test ===")
    print("This will monitor GPU usage for 30 seconds...")
    print("Try opening a video, game, or running a GPU-intensive task")
    print()
    
    # Initialize metrics collector
    metrics = MetricsCollector()
    
    start_time = time.time()
    duration = 30  # 30 seconds
    
    max_utilization = 0
    readings_count = 0
    
    while time.time() - start_time < duration:
        try:
            # Get GPU metrics
            gpu_data = metrics.get_gpu_metrics()
            
            if gpu_data:
                for i, gpu in enumerate(gpu_data):
                    util = gpu.get('utilization_gpu', 0)
                    temp = gpu.get('temperature', 0)
                    name = gpu.get('name', 'Unknown')
                    
                    max_utilization = max(max_utilization, util)
                    readings_count += 1
                    
                    print(f"[{time.strftime('%H:%M:%S')}] GPU {i} ({name}): {util}% utilization, {temp}°C")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No GPU data available")
            
            time.sleep(1)  # Update every second
            
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)
    
    print(f"\n=== Summary ===")
    print(f"Max GPU utilization seen: {max_utilization}%")
    print(f"Total readings: {readings_count}")
    
    if max_utilization == 0:
        print("\nTroubleshooting tips:")
        print("1. Try opening a video in your browser")
        print("2. Run a graphics-intensive application")
        print("3. Check if Windows Game Mode is affecting readings")
        print("4. Ensure you're using the dedicated GPU if available")

if __name__ == "__main__":
    main()
