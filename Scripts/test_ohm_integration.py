"""
Test OpenHardwareMonitor Integration
Quick test to verify OHM is working correctly
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from devicepilot.core.ohm_monitor import get_hardware_monitor
from devicepilot.core.metrics import MetricsCollector
import time
import json

def test_ohm_direct():
    """Test OpenHardwareMonitor directly"""
    print("=== Testing OpenHardwareMonitor Direct Access ===")
    
    monitor = get_hardware_monitor()
    if not monitor:
        print("❌ OpenHardwareMonitor not available")
        return False
    
    print("✅ OpenHardwareMonitor initialized successfully")
    
    # Get all sensor data
    print("\n--- All Sensors ---")
    all_data = monitor.get_all_sensors()
    
    if all_data:
        print(f"Temperature sensors found: {len(all_data.get('temperatures', {}))}")
        print(f"Fan sensors found: {len(all_data.get('fans', {}))}")
        print(f"Voltage sensors found: {len(all_data.get('voltages', {}))}")
        print(f"Load sensors found: {len(all_data.get('loads', {}))}")
        
        # Show summary
        summary = all_data.get('summary', {})
        print(f"\nTemperature Summary:")
        print(f"  CPU: {summary.get('cpu_temp', 0):.1f}°C")
        print(f"  GPU: {summary.get('gpu_temp', 0):.1f}°C")
        print(f"  Motherboard: {summary.get('motherboard_temp', 0):.1f}°C")
        print(f"  Highest: {summary.get('highest_temp', 0):.1f}°C")
        print(f"  Average: {summary.get('average_temp', 0):.1f}°C")
        
        # Show critical sensors
        critical = summary.get('critical_sensors', [])
        if critical:
            print(f"\n⚠️ Critical temperature warnings: {len(critical)}")
            for sensor in critical:
                print(f"  {sensor.get('sensor', 'Unknown')}: {sensor.get('temp', 0):.1f}°C")
        else:
            print("✅ All temperatures within safe limits")
        
        return True
    else:
        print("❌ No sensor data retrieved")
        return False

def test_metrics_integration():
    """Test MetricsCollector with OHM integration"""
    print("\n=== Testing MetricsCollector Integration ===")
    
    collector = MetricsCollector()
    
    print("Getting temperature metrics...")
    temp_data = collector.get_temperature_metrics()
    
    if temp_data.get('sensors'):
        print("✅ Temperature data retrieved via MetricsCollector")
        print(f"Sensors found: {len(temp_data['sensors'])}")
        
        summary = temp_data.get('summary', {})
        print(f"CPU Temperature: {summary.get('cpu_temp', 0):.1f}°C")
        print(f"GPU Temperature: {summary.get('gpu_temp', 0):.1f}°C")
        
        return True
    else:
        print("❌ No temperature data from MetricsCollector")
        return False

def test_gpu_data():
    """Test GPU data retrieval"""
    print("\n=== Testing GPU Data ===")
    
    monitor = get_hardware_monitor()
    if not monitor:
        print("❌ OpenHardwareMonitor not available")
        return False
    
    gpu_data = monitor.get_gpu_data()
    
    if gpu_data:
        print(f"✅ Found {len(gpu_data)} GPU(s)")
        for i, gpu in enumerate(gpu_data):
            print(f"\nGPU {i+1}:")
            print(f"  Name: {gpu.get('name', 'Unknown')}")
            print(f"  Vendor: {gpu.get('vendor', 'Unknown')}")
            print(f"  Temperature: {gpu.get('temperature', 0)}°C")
            print(f"  Load: {gpu.get('utilization_gpu', 0)}%")
            print(f"  Memory Total: {gpu.get('memory_total_mb', 0):.1f}MB")
        return True
    else:
        print("❌ No GPU data found")
        return False

def main():
    """Main test function"""
    print("OpenHardwareMonitor Integration Test")
    print("=" * 50)
    
    # Run tests
    tests = [
        ("Direct OHM Access", test_ohm_direct),
        ("MetricsCollector Integration", test_metrics_integration),
        ("GPU Data Retrieval", test_gpu_data)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
        
        print("-" * 30)
    
    print(f"\nTest Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! OpenHardwareMonitor integration is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
