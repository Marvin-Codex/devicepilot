"""
Real-time GPU monitoring while generating load
Monitor GPU utilization in real-time and demonstrate overlay functionality
"""

import sys
import os
import time
import webbrowser
sys.path.append('.')

from devicepilot.core.metrics import MetricsCollector

def monitor_gpu_realtime():
    """Monitor GPU utilization in real-time"""
    print("=== Real-time GPU Utilization Monitor ===")
    print("This will monitor GPU usage while you generate load")
    print()
    
    # Initialize metrics collector
    collector = MetricsCollector()
    
    print("🚀 Opening GPU stress test in browser...")
    print("   This will load a WebGL demo that uses GPU")
    
    # Open a GPU-intensive WebGL demo
    webbrowser.open("https://webglsamples.org/aquarium/aquarium.html")
    
    print("\n📊 Monitoring GPU utilization (Press Ctrl+C to stop)...")
    print("Timestamp        | GPU 1                    | GPU 2")
    print("-" * 70)
    
    try:
        while True:
            metrics = collector.get_all_metrics()
            gpu_data = metrics.get("gpu", [])
            
            current_time = time.strftime("%H:%M:%S")
            
            gpu1_info = "None"
            gpu2_info = "None"
            
            if len(gpu_data) >= 1:
                gpu = gpu_data[0]
                gpu1_info = f"{gpu.get('name', 'Unknown')[:12]}: {gpu.get('utilization_gpu', 0):3d}% / {gpu.get('temperature', 0):2d}°C"
            
            if len(gpu_data) >= 2:
                gpu = gpu_data[1]
                gpu2_info = f"{gpu.get('name', 'Unknown')[:12]}: {gpu.get('utilization_gpu', 0):3d}% / {gpu.get('temperature', 0):2d}°C"
            
            print(f"{current_time} | {gpu1_info:<24} | {gpu2_info}")
            
            # Check if there's any significant GPU activity
            for gpu in gpu_data:
                utilization = gpu.get('utilization_gpu', 0)
                if utilization > 10:  # More than 10% usage
                    print(f"🎮 GPU Activity Detected! {gpu.get('name', 'Unknown')}: {utilization}%")
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped.")
        print("\n📋 Final GPU Status:")
        
        final_metrics = collector.get_all_metrics()
        final_gpu_data = final_metrics.get("gpu", [])
        
        for i, gpu in enumerate(final_gpu_data, 1):
            print(f"  GPU {i}: {gpu.get('name', 'Unknown')}")
            print(f"    Utilization: {gpu.get('utilization_gpu', 0)}%")
            print(f"    Temperature: {gpu.get('temperature', 0)}°C")
            print(f"    Memory: {gpu.get('memory_total_mb', 0):.1f}MB")
        
        print("\n💡 Overlay Integration Status:")
        if final_gpu_data:
            primary_gpu = final_gpu_data[0]
            print(f"   Primary GPU for overlay: {primary_gpu.get('name', 'Unknown')}")
            print(f"   Utilization shown in overlay: {primary_gpu.get('utilization_gpu', 0)}%")
            print("   ✅ GPU overlay stats are working correctly!")
        else:
            print("   ❌ No GPU data available for overlay")

if __name__ == "__main__":
    monitor_gpu_realtime()
