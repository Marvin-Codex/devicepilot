"""
OpenHardwareMonitor Integration
Professional hardware monitoring using OpenHardwareMonitorLib.dll
Provides accurate temperature, fan, voltage, and load readings
"""

import os
import sys
from typing import Dict, Optional, List
from pathlib import Path

# Try to import pythonnet and load OpenHardwareMonitorLib
OHM_AVAILABLE = False
try:
    import clr
    
    # Get the path to the DLL (it's in devicepilot/libs, not devicepilot/core/libs)
    current_dir = Path(__file__).parent.parent  # Go up from core to devicepilot
    dll_path = current_dir / "libs" / "OpenHardwareMonitorLib.dll"
    
    if dll_path.exists():
        # Add reference to the DLL
        clr.AddReference(str(dll_path))
        from OpenHardwareMonitor import Hardware # type: ignore
        OHM_AVAILABLE = True
        print("OpenHardwareMonitor library loaded successfully")
    else:
        print(f"OpenHardwareMonitorLib.dll not found at: {dll_path}")
        
except ImportError as e:
    print(f"Failed to import pythonnet: {e}")
    print("Install with: pip install pythonnet")
except Exception as e:
    print(f"Failed to load OpenHardwareMonitorLib: {e}")


class OpenHardwareMonitor:
    """Hardware monitoring using OpenHardwareMonitorLib"""
    
    def __init__(self):
        self.computer = None
        self.initialized = False
        
        if OHM_AVAILABLE:
            try:
                self.computer = Hardware.Computer()
                
                # Enable all hardware monitoring
                self.computer.MainboardEnabled = True
                self.computer.CPUEnabled = True
                self.computer.GPUEnabled = True
                self.computer.RAMEnabled = True
                self.computer.FanControllerEnabled = True
                self.computer.HDDEnabled = True
                
                self.computer.Open()
                self.initialized = True
                print("OpenHardwareMonitor initialized successfully")
                
            except Exception as e:
                print(f"Failed to initialize OpenHardwareMonitor: {e}")
                self.initialized = False
        else:
            print("OpenHardwareMonitor not available")

    def get_all_sensors(self) -> Dict:
        """Get all sensor data from OpenHardwareMonitor"""
        if not self.initialized:
            return {}
        
        try:
            sensors_data = {
                "temperatures": {},
                "fans": {},
                "voltages": {},
                "loads": {},
                "clocks": {},
                "powers": {},
                "summary": {
                    "cpu_temp": 0,
                    "gpu_temp": 0,
                    "motherboard_temp": 0,
                    "highest_temp": 0,
                    "average_temp": 0,
                    "critical_sensors": []
                }
            }
            
            all_temps = []
            
            # Update all hardware
            for hardware in self.computer.Hardware:
                hardware.Update()
                hardware_name = str(hardware.Name)
                
                # Process each sensor
                for sensor in hardware.Sensors:
                    if sensor.Value is None:
                        continue
                    
                    sensor_name = str(sensor.Name)
                    sensor_type = str(sensor.SensorType)
                    sensor_value = float(sensor.Value)
                    
                    sensor_info = {
                        "hardware": hardware_name,
                        "name": sensor_name,
                        "value": sensor_value,
                        "unit": self._get_sensor_unit(sensor_type)
                    }
                    
                    # Categorize sensors by type
                    if sensor_type == "Temperature":
                        if hardware_name not in sensors_data["temperatures"]:
                            sensors_data["temperatures"][hardware_name] = []
                        sensors_data["temperatures"][hardware_name].append(sensor_info)
                        all_temps.append(sensor_value)
                        
                        # Update summary temperatures
                        self._update_temperature_summary(hardware_name, sensor_name, sensor_value, sensors_data["summary"])
                        
                        # Check for critical temperatures
                        if sensor_value > 85:  # Critical threshold
                            sensors_data["summary"]["critical_sensors"].append({
                                "sensor": f"{hardware_name} - {sensor_name}",
                                "temp": sensor_value,
                                "critical": 85.0
                            })
                    
                    elif sensor_type == "Fan":
                        if hardware_name not in sensors_data["fans"]:
                            sensors_data["fans"][hardware_name] = []
                        sensors_data["fans"][hardware_name].append(sensor_info)
                    
                    elif sensor_type == "Voltage":
                        if hardware_name not in sensors_data["voltages"]:
                            sensors_data["voltages"][hardware_name] = []
                        sensors_data["voltages"][hardware_name].append(sensor_info)
                    
                    elif sensor_type == "Load":
                        if hardware_name not in sensors_data["loads"]:
                            sensors_data["loads"][hardware_name] = []
                        sensors_data["loads"][hardware_name].append(sensor_info)
                    
                    elif sensor_type == "Clock":
                        if hardware_name not in sensors_data["clocks"]:
                            sensors_data["clocks"][hardware_name] = []
                        sensors_data["clocks"][hardware_name].append(sensor_info)
                    
                    elif sensor_type == "Power":
                        if hardware_name not in sensors_data["powers"]:
                            sensors_data["powers"][hardware_name] = []
                        sensors_data["powers"][hardware_name].append(sensor_info)
            
            # Calculate temperature summary
            if all_temps:
                sensors_data["summary"]["highest_temp"] = max(all_temps)
                sensors_data["summary"]["average_temp"] = round(sum(all_temps) / len(all_temps), 1)
            
            return sensors_data
            
        except Exception as e:
            print(f"Error getting sensor data: {e}")
            return {}

    def get_temperature_data(self) -> Dict:
        """Get only temperature data in the format expected by the overlay"""
        all_data = self.get_all_sensors()
        
        if not all_data:
            return {}
        
        # Convert to the format expected by the existing temperature system
        temperature_data = {
            "sensors": {},
            "summary": all_data.get("summary", {})
        }
        
        temperatures = all_data.get("temperatures", {})
        for hardware_name, sensors in temperatures.items():
            temperature_data["sensors"][hardware_name] = []
            for sensor in sensors:
                temperature_data["sensors"][hardware_name].append({
                    "label": sensor["name"],
                    "current": sensor["value"],
                    "high": 80.0 if sensor["value"] > 0 else None,  # Estimated safe threshold
                    "critical": 90.0 if sensor["value"] > 0 else None  # Estimated critical threshold
                })
        
        return temperature_data

    def _get_sensor_unit(self, sensor_type: str) -> str:
        """Get the unit for a sensor type"""
        units = {
            "Temperature": "°C",
            "Fan": "RPM", 
            "Voltage": "V",
            "Load": "%",
            "Clock": "MHz",
            "Power": "W",
            "Data": "GB",
            "SmallData": "MB"
        }
        return units.get(sensor_type, "")

    def _update_temperature_summary(self, hardware_name: str, sensor_name: str, value: float, summary: Dict):
        """Update temperature summary with categorized temperatures"""
        hardware_lower = hardware_name.lower()
        sensor_lower = sensor_name.lower()
        
        # GPU temperature detection (check first since it can contain "core" too)
        if any(keyword in hardware_lower for keyword in ["gpu", "graphics", "video", "nvidia", "amd", "radeon", "geforce"]):
            summary["gpu_temp"] = max(summary["gpu_temp"], value)
        
        # CPU temperature detection
        elif any(keyword in hardware_lower or keyword in sensor_lower 
               for keyword in ["cpu", "processor"]) or (
               "core" in sensor_lower and "gpu" not in sensor_lower and "graphics" not in hardware_lower):
            summary["cpu_temp"] = max(summary["cpu_temp"], value)
        
        # Motherboard/System temperature detection
        elif any(keyword in hardware_lower or keyword in sensor_lower 
                for keyword in ["motherboard", "mainboard", "system", "chipset", "ambient", "chassis"]):
            summary["motherboard_temp"] = max(summary["motherboard_temp"], value)
        
        # If it's an SSD or storage device, consider it system temperature
        elif any(keyword in hardware_lower for keyword in ["ssd", "hdd", "hard disk", "storage"]):
            summary["motherboard_temp"] = max(summary["motherboard_temp"], value)

    def get_cpu_load(self) -> float:
        """Get CPU load percentage"""
        if not self.initialized:
            return 0.0
        
        try:
            for hardware in self.computer.Hardware:
                hardware.Update()
                if "cpu" in str(hardware.Name).lower():
                    for sensor in hardware.Sensors:
                        if (str(sensor.SensorType) == "Load" and 
                            "total" in str(sensor.Name).lower()):
                            return float(sensor.Value) if sensor.Value else 0.0
        except Exception as e:
            print(f"Error getting CPU load: {e}")
        
        return 0.0

    def get_gpu_data(self) -> List[Dict]:
        """Get GPU data including temperature, load, and memory with improved accuracy"""
        if not self.initialized:
            return []
        
        gpus = []
        
        try:
            # First pass: Identify GPU hardware and collect basic info
            gpu_hardware = {}
            
            for hardware in self.computer.Hardware:
                hardware.Update()
                hardware_name = str(hardware.Name)
                
                # Check if this is a GPU (exclude CPUs and improve detection)
                hardware_lower = hardware_name.lower()
                
                # Enhanced GPU detection - prioritize discrete graphics
                is_discrete_gpu = any(keyword in hardware_lower for keyword in [
                    "geforce", "gtx", "rtx",  # NVIDIA discrete
                    "radeon hd", "radeon rx", "radeon pro",  # AMD discrete
                    "arc", "xe"  # Intel discrete
                ])
                
                # Integrated graphics detection
                is_integrated_gpu = any(keyword in hardware_lower for keyword in [
                    "radeon r4", "radeon r5", "radeon r6", "radeon r7",  # AMD APU graphics
                    "uhd graphics", "iris", "hd graphics",  # Intel integrated
                    "vega"  # AMD Vega integrated
                ]) and "graphics" in hardware_lower
                
                # CPU exclusion - be more specific
                is_cpu = any(cpu_keyword in hardware_lower for cpu_keyword in [
                    "a4-", "a6-", "a8-", "a10-", "a12-", "fx-", "ryzen", "core i", "pentium", "celeron",
                    "athlon", "phenom", "sempron", "opteron", "epyc", "threadripper"
                ])
                
                # Final GPU determination
                is_gpu = (is_discrete_gpu or is_integrated_gpu) and not is_cpu

                if is_gpu:
                    gpu_hardware[hardware_name] = {
                        "hardware": hardware,
                        "is_discrete": is_discrete_gpu,
                        "data": {
                            "name": hardware_name,
                            "temperature": 0,
                            "load": 0,
                            "memory_used": 0,
                            "memory_total": 0,
                            "fan_speed": 0,
                            "clock_core": 0,
                            "clock_memory": 0,
                            "power": 0
                        }
                    }
            
            # Second pass: Collect sensor data with multiple updates for better accuracy
            for gpu_name, gpu_info in gpu_hardware.items():
                hardware = gpu_info["hardware"]
                gpu_data = gpu_info["data"]
                
                # Update multiple times to get more accurate readings
                load_readings = []
                temp_readings = []
                
                for update_cycle in range(3):  # Multiple readings for accuracy
                    hardware.Update()
                    
                    for sensor in hardware.Sensors:
                        if sensor.Value is None:
                            continue
                        
                        sensor_name = str(sensor.Name).lower()
                        sensor_type = str(sensor.SensorType)
                        value = float(sensor.Value)
                        
                        if sensor_type == "Temperature":
                            if any(keyword in sensor_name for keyword in ["gpu", "core", "junction", "edge"]):
                                temp_readings.append(value)
                                if value > gpu_data["temperature"]:
                                    gpu_data["temperature"] = value
                        
                        elif sensor_type == "Load":
                            # More comprehensive GPU load detection
                            if any(keyword in sensor_name for keyword in ["gpu", "core", "3d", "graphics"]):
                                # Prioritize specific GPU load sensors
                                if "gpu" in sensor_name or "3d" in sensor_name:
                                    load_readings.append(value)
                                    gpu_data["load"] = value  # Direct assignment for GPU-specific sensors
                                elif "core" in sensor_name and gpu_data["load"] == 0:
                                    load_readings.append(value)
                                    gpu_data["load"] = value  # Fallback to core load if no GPU-specific found
                        
                        elif sensor_type == "SmallData" or sensor_type == "Data":
                            if "memory" in sensor_name:
                                if "used" in sensor_name:
                                    gpu_data["memory_used"] = value
                                elif "total" in sensor_name or "free" in sensor_name:
                                    gpu_data["memory_total"] = value
                        
                        elif sensor_type == "Fan":
                            gpu_data["fan_speed"] = max(gpu_data["fan_speed"], value)
                        
                        elif sensor_type == "Clock":
                            if "core" in sensor_name or "gpu" in sensor_name:
                                gpu_data["clock_core"] = max(gpu_data["clock_core"], value)
                            elif "memory" in sensor_name:
                                gpu_data["clock_memory"] = max(gpu_data["clock_memory"], value)
                        
                        elif sensor_type == "Power":
                            if "gpu" in sensor_name or "total" in sensor_name:
                                gpu_data["power"] = max(gpu_data["power"], value)
                
                # Use average or max of readings for better accuracy
                if load_readings:
                    gpu_data["load"] = max(load_readings)  # Use max load reading
                
                # Convert to format expected by overlay
                formatted_gpu = {
                    "vendor": ("NVIDIA" if "nvidia" in gpu_data["name"].lower() or "geforce" in gpu_data["name"].lower()
                              else "AMD" if "amd" in gpu_data["name"].lower() or "radeon" in gpu_data["name"].lower()
                              else "Intel" if "intel" in gpu_data["name"].lower()
                              else "Unknown"),
                    "name": gpu_data["name"],
                    "memory_total": int(gpu_data["memory_total"] * 1024 * 1024) if gpu_data["memory_total"] > 0 else 0,
                    "memory_total_mb": gpu_data["memory_total"] * 1024 if gpu_data["memory_total"] > 0 else 0,
                    "utilization_gpu": int(round(gpu_data["load"])),
                    "utilization_memory": 0,  # Calculate if possible
                    "temperature": int(round(gpu_data["temperature"])),
                    "power_watts": round(gpu_data["power"], 1),
                    "clock_graphics_mhz": int(gpu_data["clock_core"]),
                    "clock_memory_mhz": int(gpu_data["clock_memory"]),
                    "fan_speed_rpm": int(gpu_data["fan_speed"]),
                    "is_active": gpu_data["temperature"] > 30 or gpu_data["load"] > 0,  # GPU is active if it has reasonable temp or load
                    "is_discrete": gpu_info["is_discrete"]
                }
                
                gpus.append(formatted_gpu)
                
        except Exception as e:
            print(f"Error getting GPU data: {e}")
        
        # Sort GPUs to prioritize active and discrete ones
        gpus.sort(key=lambda x: (
            -int(x.get("is_discrete", False)),  # Discrete GPUs first
            -x.get("utilization_gpu", 0),       # Higher utilization first
            -x.get("temperature", 0),           # Higher temperature first
            -len(x.get("name", ""))             # Longer names (usually more descriptive) first
        ))
        
        return gpus

    def close(self):
        """Close the hardware monitor"""
        if self.computer:
            try:
                self.computer.Close()
            except:
                pass
            self.computer = None
            self.initialized = False

    def __del__(self):
        """Cleanup on destruction"""
        self.close()


# Global instance
_ohm_instance = None

def get_hardware_monitor() -> Optional[OpenHardwareMonitor]:
    """Get global OpenHardwareMonitor instance"""
    global _ohm_instance
    
    if _ohm_instance is None and OHM_AVAILABLE:
        _ohm_instance = OpenHardwareMonitor()
    
    return _ohm_instance if _ohm_instance and _ohm_instance.initialized else None
