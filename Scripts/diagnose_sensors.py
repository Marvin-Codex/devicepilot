"""
Diagnostic test to see exactly what sensors OpenHardwareMonitor is detecting
This will help us understand why GPU and system temperatures aren't showing
"""

import sys
import os
sys.path.append('.')

from devicepilot.core.ohm_monitor import get_hardware_monitor

def diagnose_sensors():
    """Diagnose what sensors are being detected"""
    print("=== OpenHardwareMonitor Sensor Diagnostic ===")
    
    monitor = get_hardware_monitor()
    if not monitor:
        print("❌ OpenHardwareMonitor not available")
        return
    
    print("✅ OpenHardwareMonitor initialized")
    
    all_data = monitor.get_all_sensors()
    if not all_data:
        print("❌ No sensor data available")
        return
    
    print("\n=== DETAILED SENSOR ANALYSIS ===")
    
    # Show all temperature sensors with their exact names
    temperatures = all_data.get("temperatures", {})
    print(f"\n🌡️ TEMPERATURE SENSORS FOUND: {len(temperatures)}")
    
    for hardware_name, sensors in temperatures.items():
        print(f"\n📋 Hardware: '{hardware_name}'")
        print(f"   Hardware name (lowercase): '{hardware_name.lower()}'")
        
        for sensor in sensors:
            sensor_name = sensor.get("name", "Unknown")
            sensor_value = sensor.get("value", 0)
            print(f"   • Sensor: '{sensor_name}' = {sensor_value:.1f}°C")
            print(f"     Sensor name (lowercase): '{sensor_name.lower()}'")
            
            # Check categorization (updated to match the fixed logic)
            hardware_lower = hardware_name.lower()
            sensor_lower = sensor_name.lower()
            
            category = "❓ Unknown"
            
            # GPU temperature detection (check first since it can contain "core" too)
            if any(keyword in hardware_lower for keyword in ["gpu", "graphics", "video", "nvidia", "amd", "radeon", "geforce"]):
                category = "🎮 GPU"
            # CPU temperature detection
            elif any(keyword in hardware_lower or keyword in sensor_lower 
                   for keyword in ["cpu", "processor"]) or (
                   "core" in sensor_lower and "gpu" not in sensor_lower and "graphics" not in hardware_lower):
                category = "🔥 CPU"
            # Motherboard/System temperature detection
            elif any(keyword in hardware_lower or keyword in sensor_lower 
                    for keyword in ["motherboard", "mainboard", "system", "chipset", "ambient", "chassis"]):
                category = "💾 Motherboard/System"
            # If it's an SSD or storage device, consider it system temperature
            elif any(keyword in hardware_lower for keyword in ["ssd", "hdd", "hard disk", "storage"]):
                category = "💾 Storage/System"
                
            print(f"     Category: {category}")
    
    # Show summary
    summary = all_data.get("summary", {})
    print(f"\n📊 TEMPERATURE SUMMARY:")
    print(f"   CPU Temperature: {summary.get('cpu_temp', 0):.1f}°C")
    print(f"   GPU Temperature: {summary.get('gpu_temp', 0):.1f}°C")
    print(f"   Motherboard Temperature: {summary.get('motherboard_temp', 0):.1f}°C")
    print(f"   Highest Temperature: {summary.get('highest_temp', 0):.1f}°C")
    print(f"   Average Temperature: {summary.get('average_temp', 0):.1f}°C")
    
    # Show load sensors (might help identify GPU)
    loads = all_data.get("loads", {})
    print(f"\n📊 LOAD SENSORS FOUND: {len(loads)}")
    
    for hardware_name, sensors in loads.items():
        print(f"\n📋 Hardware: '{hardware_name}'")
        for sensor in sensors:
            sensor_name = sensor.get("name", "Unknown")
            sensor_value = sensor.get("value", 0)
            print(f"   • Load: '{sensor_name}' = {sensor_value:.1f}%")
    
    # Check if we missed any categorization
    print(f"\n🔍 CATEGORIZATION ANALYSIS:")
    print(f"Keywords checked for GPU: gpu, graphics, video, nvidia, amd, radeon, geforce")
    print(f"Keywords checked for System: motherboard, mainboard, system, chipset")
    print(f"Keywords checked for CPU: cpu, processor, core")
    
    # Show specific suggestions
    print(f"\n💡 SUGGESTIONS:")
    if summary.get('gpu_temp', 0) == 0:
        print("   • GPU temperature not detected. Check if:")
        print("     - GPU hardware names contain expected keywords")
        print("     - GPU sensors have temperature readings")
        print("     - GPU drivers are properly installed")
    
    if summary.get('motherboard_temp', 0) == 0:
        print("   • System/Motherboard temperature not detected. Check if:")
        print("     - Motherboard sensors are enabled in BIOS")
        print("     - Hardware names contain system-related keywords")

if __name__ == "__main__":
    diagnose_sensors()
