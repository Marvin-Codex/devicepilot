"""
Advanced System Metrics Collector
Collects CPU, RAM, GPU, battery, and FPS metrics with error handling
"""

import psutil
import time
import subprocess
import platform
from typing import Dict, Optional, List
import json
import os

# GPU monitoring imports
try:
    from pynvml import *  # Import all NVIDIA functions
    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    wmi = None

# Import OpenHardwareMonitor integration
try:
    from .ohm_monitor import get_hardware_monitor
    OHM_AVAILABLE = True
except ImportError:
    OHM_AVAILABLE = False


class MetricsCollector:
    def __init__(self):
        self.nvidia_initialized = False
        self.wmi_connection = None
        self.last_cpu_times = None
        self.last_timestamp = None
        self.ohm_monitor = None
        
        # Initialize GPU monitoring
        self._init_gpu_monitoring()
        
        # Initialize OpenHardwareMonitor
        self._init_ohm_monitoring()

    def _init_gpu_monitoring(self):
        """Initialize GPU monitoring capabilities"""
        if NVIDIA_AVAILABLE:
            try:
                nvmlInit()
                self.nvidia_initialized = True
                print("NVIDIA GPU monitoring initialized")
            except Exception as e:
                print(f"Failed to initialize NVIDIA monitoring: {e}")
        
        if WMI_AVAILABLE and wmi:
            try:
                self.wmi_connection = wmi.WMI()
                print("WMI GPU monitoring initialized")
            except Exception as e:
                print(f"Failed to initialize WMI: {e}")
                self.wmi_connection = None

    def _init_ohm_monitoring(self):
        """Initialize OpenHardwareMonitor"""
        if OHM_AVAILABLE:
            try:
                self.ohm_monitor = get_hardware_monitor()
                if self.ohm_monitor:
                    print("OpenHardwareMonitor initialized successfully")
                else:
                    print("OpenHardwareMonitor failed to initialize")
            except Exception as e:
                print(f"Error initializing OpenHardwareMonitor: {e}")
                self.ohm_monitor = None

    def get_all_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        return {
            "cpu": self.get_cpu_metrics(),
            "memory": self.get_memory_metrics(),
            "gpu": self.get_gpu_metrics(),
            "battery": self.get_battery_metrics(),
            "temperature": self.get_temperature_metrics(),
            "fps": self.get_fps_metrics(),
            "system": self.get_system_info()
        }

    def get_cpu_metrics(self) -> Dict:
        """Get detailed CPU metrics"""
        try:
            # CPU percentage with per-core breakdown
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            
            # CPU count
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False)
            
            # Load average (if available)
            load_avg = None
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
            
            return {
                "usage_percent": round(cpu_percent, 1),
                "usage_per_core": [round(x, 1) for x in cpu_per_core],
                "frequency_current": round(cpu_freq.current, 1) if cpu_freq else None,
                "frequency_max": round(cpu_freq.max, 1) if cpu_freq else None,
                "core_count_logical": cpu_count,
                "core_count_physical": cpu_count_physical,
                "load_average": load_avg
            }
        except Exception as e:
            print(f"Error getting CPU metrics: {e}")
            return {"usage_percent": 0, "error": str(e)}

    def get_memory_metrics(self) -> Dict:
        """Get detailed memory metrics"""
        try:
            # Virtual memory
            virtual_mem = psutil.virtual_memory()
            
            # Swap memory
            swap_mem = psutil.swap_memory()
            
            return {
                "total": virtual_mem.total,
                "available": virtual_mem.available,
                "used": virtual_mem.used,
                "percentage": round(virtual_mem.percent, 1),
                "free": virtual_mem.free,
                "buffers": getattr(virtual_mem, 'buffers', 0),
                "cached": getattr(virtual_mem, 'cached', 0),
                "swap": {
                    "total": swap_mem.total,
                    "used": swap_mem.used,
                    "free": swap_mem.free,
                    "percentage": round(swap_mem.percent, 1)
                }
            }
        except Exception as e:
            print(f"Error getting memory metrics: {e}")
            return {"percentage": 0, "error": str(e)}

    def get_gpu_metrics(self) -> List[Dict]:
        """Get GPU metrics for all available GPUs with improved accuracy"""
        gpus = []
        
        # Try PowerShell method first (most accurate, matches Task Manager)
        if platform.system() == "Windows":
            ps_gpus = self.get_gpu_metrics_via_powershell()
            if ps_gpus:
                print(f"Using PowerShell GPU data: {len(ps_gpus)} GPU(s) found")
                # Enhance with temperature data from OpenHardwareMonitor
                if self.ohm_monitor:
                    try:
                        ohm_gpus = self.ohm_monitor.get_gpu_data()
                        # Merge temperature data
                        for ps_gpu in ps_gpus:
                            for ohm_gpu in ohm_gpus:
                                if ohm_gpu.get('is_active', False):  # Use active GPU temp
                                    ps_gpu['temperature'] = ohm_gpu.get('temperature', 0)
                                    ps_gpu['name'] = ohm_gpu.get('name', ps_gpu['name'])
                                    ps_gpu['vendor'] = ohm_gpu.get('vendor', ps_gpu['vendor'])
                                    break
                    except Exception as e:
                        print(f"Failed to enhance PowerShell data with OHM temps: {e}")
                
                return ps_gpus
        
        # Fallback: Try OpenHardwareMonitor with validation
        if self.ohm_monitor:
            try:
                ohm_gpus = self.ohm_monitor.get_gpu_data()
                if ohm_gpus:
                    print(f"Using OpenHardwareMonitor GPU data: {len(ohm_gpus)} GPU(s) found")
                    
                    # Validate OHM readings - if utilization seems wrong, try to correct it
                    validated_gpus = []
                    for gpu in ohm_gpus:
                        gpu_util = gpu.get('utilization_gpu', 0)
                        
                        # If OHM reports 100% or very high usage, try to validate with PowerShell
                        if gpu_util >= 90 and platform.system() == "Windows":
                            try:
                                ps_validation = self.get_gpu_metrics_via_powershell()
                                if ps_validation:
                                    # Use PowerShell reading instead
                                    max_ps_util = max(g.get('utilization_gpu', 0) for g in ps_validation)
                                    if max_ps_util < 50:  # Significant difference
                                        print(f"OHM reported {gpu_util}%, PowerShell shows {max_ps_util}% - using PowerShell")
                                        gpu['utilization_gpu'] = max_ps_util
                            except:
                                pass
                        
                        validated_gpus.append(gpu)
                    
                    # Debug: Print utilization values
                    for i, gpu in enumerate(validated_gpus):
                        util = gpu.get('utilization_gpu', 0)
                        temp = gpu.get('temperature', 0)
                        print(f"  GPU {i} ({gpu.get('name', 'Unknown')}): {util}% utilization, {temp}°C")
                    
                    # Filter out inactive GPUs unless no active ones are found
                    active_gpus = [gpu for gpu in validated_gpus if gpu.get('utilization_gpu', 0) > 0 or gpu.get('temperature', 0) > 30]
                    
                    if active_gpus:
                        print(f"Found {len(active_gpus)} active GPU(s)")
                        return active_gpus
                    elif validated_gpus:
                        print("No active GPUs found, returning all detected GPUs")
                        # Return all GPUs but prioritize those with temperature readings
                        return sorted(validated_gpus, key=lambda x: (-x.get('temperature', 0), -x.get('utilization_gpu', 0)))
            except Exception as e:
                print(f"Error getting OHM GPU data: {e}")
        
        # Fallback to NVIDIA GPUs
        if self.nvidia_initialized:
            nvidia_gpus = self._get_nvidia_gpu_metrics()
            if nvidia_gpus:
                print(f"Using NVIDIA GPU data: {len(nvidia_gpus)} GPU(s) found")
                gpus.extend(nvidia_gpus)
        
        # AMD/Intel GPUs via WMI (Windows only) - only if no other source found
        if not gpus and self.wmi_connection and platform.system() == "Windows":
            wmi_gpus = self._get_wmi_gpu_metrics()
            if wmi_gpus:
                print(f"Using WMI GPU data: {len(wmi_gpus)} GPU(s) found")
                gpus.extend(wmi_gpus)
        
        return gpus

    def _get_nvidia_gpu_metrics(self) -> List[Dict]:
        """Get NVIDIA GPU metrics using NVML"""
        gpus = []
        try:
            device_count = nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = nvmlDeviceGetHandleByIndex(i)
                
                # Basic info
                name = nvmlDeviceGetName(handle).decode('utf-8')
                
                # Utilization
                try:
                    utilization = nvmlDeviceGetUtilizationRates(handle)
                    gpu_util = utilization.gpu
                    memory_util = utilization.memory
                except:
                    gpu_util = 0
                    memory_util = 0
                
                # Memory info
                try:
                    memory_info = nvmlDeviceGetMemoryInfo(handle)
                    memory_used = memory_info.used
                    memory_total = memory_info.total
                except:
                    memory_used = 0
                    memory_total = 0
                
                # Temperature
                try:
                    temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
                except:
                    temp = 0
                
                # Power
                try:
                    power = nvmlDeviceGetPowerUsage(handle) / 1000  # Convert to watts
                except:
                    power = 0
                
                # Clock speeds
                try:
                    graphics_clock = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_GRAPHICS)
                    memory_clock = nvmlDeviceGetClockInfo(handle, NVML_CLOCK_MEM)
                except:
                    graphics_clock = 0
                    memory_clock = 0
                
                gpus.append({
                    "vendor": "NVIDIA",
                    "name": name,
                    "index": i,
                    "utilization_gpu": gpu_util,
                    "utilization_memory": memory_util,
                    "memory_used": memory_used,
                    "memory_total": memory_total,
                    "memory_used_mb": round(memory_used / (1024**2), 1),
                    "memory_total_mb": round(memory_total / (1024**2), 1),
                    "temperature": temp,
                    "power_watts": round(power, 1),
                    "clock_graphics_mhz": graphics_clock,
                    "clock_memory_mhz": memory_clock
                })
        
        except Exception as e:
            print(f"Error getting NVIDIA GPU metrics: {e}")
        
        return gpus

    def _get_wmi_gpu_metrics(self) -> List[Dict]:
        """Get GPU metrics via WMI (for AMD/Intel GPUs on Windows) - Enhanced version"""
        gpus = []
        
        if not self.wmi_connection:
            return gpus
            
        try:
            # Try to access video controllers with better error handling
            video_controllers = self.wmi_connection.Win32_VideoController()
            
            for gpu in video_controllers:
                if gpu and gpu.Name and "Microsoft" not in gpu.Name:
                    
                    # Try to get more detailed performance data
                    gpu_utilization = 0
                    gpu_temperature = 0
                    
                    # Attempt to get GPU performance counters (Windows 10+)
                    try:
                        gpu_name_clean = gpu.Name.replace(" ", "_").replace("/", "_")
                        perf_query = f"SELECT * FROM Win32_PerfRawData_GPUPerformanceCounters_GPUEngine WHERE Name LIKE '%{gpu_name_clean}%'"
                        gpu_perf_data = self.wmi_connection.query(perf_query)
                        
                        for perf in gpu_perf_data:
                            if hasattr(perf, 'UtilizationPercentage'):
                                gpu_utilization = max(gpu_utilization, float(perf.UtilizationPercentage))
                    except:
                        # Performance counters not available
                        pass
                    
                    # Try alternative performance method via Win32_VideoController properties
                    try:
                        if hasattr(gpu, 'LoadPercentage') and gpu.LoadPercentage:
                            gpu_utilization = float(gpu.LoadPercentage)
                    except:
                        pass
                    
                    # Basic info available via WMI
                    gpu_info = {
                        "vendor": ("NVIDIA" if "nvidia" in gpu.Name.lower() or "geforce" in gpu.Name.lower()
                                 else "AMD" if "amd" in gpu.Name.lower() or "radeon" in gpu.Name.lower()
                                 else "Intel" if "intel" in gpu.Name.lower()
                                 else "Unknown"),
                        "name": gpu.Name,
                        "memory_total": getattr(gpu, 'AdapterRAM', 0) if hasattr(gpu, 'AdapterRAM') else 0,
                        "memory_total_mb": round(getattr(gpu, 'AdapterRAM', 0) / (1024**2), 1) if hasattr(gpu, 'AdapterRAM') else 0,
                        "utilization_gpu": int(gpu_utilization),
                        "utilization_memory": 0,
                        "temperature": int(gpu_temperature),
                        "memory_used": 0,
                        "memory_used_mb": 0
                    }
                    
                    gpus.append(gpu_info)
                    
        except Exception as e:
            # Disable WMI connection on persistent errors to prevent spam
            if "winmgmts:" in str(e):
                print(f"Disabling WMI GPU monitoring due to access error: {e}")
                self.wmi_connection = None
            else:
                print(f"Error getting WMI GPU metrics: {e}")
        
        return gpus

    def get_battery_metrics(self) -> Optional[Dict]:
        """Get battery metrics and status"""
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                return None
            
            # Calculate time remaining in a more readable format
            time_remaining_formatted = "N/A"
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                hours = battery.secsleft // 3600
                minutes = (battery.secsleft % 3600) // 60
                time_remaining_formatted = f"{hours}h {minutes}m"
            
            return {
                "percentage": round(battery.percent, 1),
                "plugged": battery.power_plugged,
                "time_remaining_seconds": battery.secsleft if battery.secsleft > 0 else None,
                "time_remaining_formatted": time_remaining_formatted,
                "status": "Charging" if battery.power_plugged else "Discharging"
            }
        except Exception as e:
            print(f"Error getting battery metrics: {e}")
            return None

    def get_temperature_metrics(self) -> Dict:
        """Get comprehensive system temperature readings with OpenHardwareMonitor priority"""
        temperatures = {
            "sensors": {},
            "summary": {
                "cpu_temp": 0,
                "gpu_temp": 0,
                "motherboard_temp": 0,
                "highest_temp": 0,
                "average_temp": 0,
                "critical_sensors": []
            }
        }
        
        try:
            # First, try OpenHardwareMonitor (most accurate)
            if self.ohm_monitor and self.ohm_monitor.initialized:
                ohm_data = self.ohm_monitor.get_temperature_data()
                if ohm_data.get("sensors"):
                    temperatures = ohm_data
                    print("Using OpenHardwareMonitor temperature data")
                    return temperatures
            
            # Fallback to psutil
            if hasattr(psutil, 'sensors_temperatures'):
                temp_sensors = psutil.sensors_temperatures()
                all_temps = []
                
                for sensor_name, sensor_list in temp_sensors.items():
                    temperatures["sensors"][sensor_name] = []
                    for sensor in sensor_list:
                        temp_info = {
                            "label": sensor.label or "Unknown",
                            "current": round(sensor.current, 1),
                            "high": sensor.high,
                            "critical": sensor.critical
                        }
                        temperatures["sensors"][sensor_name].append(temp_info)
                        all_temps.append(sensor.current)
                        
                        # Check for critical temperatures
                        if sensor.critical and sensor.current >= sensor.critical * 0.9:
                            temperatures["summary"]["critical_sensors"].append({
                                "sensor": sensor_name,
                                "label": sensor.label,
                                "temp": sensor.current,
                                "critical": sensor.critical
                            })
                        
                        # Categorize temperatures
                        sensor_lower = sensor_name.lower()
                        label_lower = (sensor.label or "").lower()
                        
                        if any(keyword in sensor_lower or keyword in label_lower 
                               for keyword in ["cpu", "core", "processor"]):
                            temperatures["summary"]["cpu_temp"] = max(
                                temperatures["summary"]["cpu_temp"], sensor.current
                            )
                        elif any(keyword in sensor_lower or keyword in label_lower 
                                for keyword in ["gpu", "video", "graphics"]):
                            temperatures["summary"]["gpu_temp"] = max(
                                temperatures["summary"]["gpu_temp"], sensor.current
                            )
                        elif any(keyword in sensor_lower or keyword in label_lower 
                                for keyword in ["motherboard", "system", "ambient"]):
                            temperatures["summary"]["motherboard_temp"] = max(
                                temperatures["summary"]["motherboard_temp"], sensor.current
                            )
                
                if all_temps:
                    temperatures["summary"]["highest_temp"] = max(all_temps)
                    temperatures["summary"]["average_temp"] = round(sum(all_temps) / len(all_temps), 1)
            
            # If no sensors found via psutil, try WMI (Windows-specific)
            if not temperatures["sensors"] and self.wmi_connection:
                wmi_temps = self._get_wmi_temperatures()
                if wmi_temps:
                    temperatures.update(wmi_temps)
                    
        except Exception as e:
            print(f"Error getting temperature metrics: {e}")
        
        return temperatures
    
    def _get_wmi_temperatures(self) -> Dict:
        """Get temperature data using WMI (Windows Management Instrumentation)"""
        temperatures = {
            "sensors": {},
            "summary": {
                "cpu_temp": 0,
                "gpu_temp": 0,
                "motherboard_temp": 0,
                "highest_temp": 0,
                "average_temp": 0,
                "critical_sensors": []
            }
        }
        
        try:
            if not self.wmi_connection:
                return temperatures
            
            all_temps = []
            
            # Get temperature from WMI thermal zones
            thermal_zones = self.wmi_connection.query("SELECT * FROM Win32_PerfRawData_Counters_ThermalZoneInformation")
            for zone in thermal_zones:
                if hasattr(zone, 'Temperature') and zone.Temperature:
                    # Convert from tenths of Kelvin to Celsius
                    temp_celsius = (zone.Temperature / 10.0) - 273.15
                    if temp_celsius > 0 and temp_celsius < 150:  # Sanity check
                        zone_name = getattr(zone, 'Name', 'Thermal Zone')
                        
                        if "thermal_zones" not in temperatures["sensors"]:
                            temperatures["sensors"]["thermal_zones"] = []
                        
                        temperatures["sensors"]["thermal_zones"].append({
                            "label": zone_name,
                            "current": round(temp_celsius, 1),
                            "high": None,
                            "critical": None
                        })
                        all_temps.append(temp_celsius)
                        
                        # Assume thermal zones are CPU-related
                        temperatures["summary"]["cpu_temp"] = max(
                            temperatures["summary"]["cpu_temp"], temp_celsius
                        )
            
            # Get CPU temperature from MSAcpi_ThermalZoneTemperature (more reliable)
            try:
                thermal_info = self.wmi_connection.query("SELECT * FROM MSAcpi_ThermalZoneTemperature")
                for temp in thermal_info:
                    if hasattr(temp, 'CurrentTemperature') and temp.CurrentTemperature:
                        # Convert from tenths of Kelvin to Celsius
                        temp_celsius = (temp.CurrentTemperature / 10.0) - 273.15
                        if temp_celsius > 0 and temp_celsius < 150:  # Sanity check
                            instance_name = getattr(temp, 'InstanceName', 'CPU Thermal Zone')
                            
                            if "cpu_thermal" not in temperatures["sensors"]:
                                temperatures["sensors"]["cpu_thermal"] = []
                            
                            temperatures["sensors"]["cpu_thermal"].append({
                                "label": instance_name,
                                "current": round(temp_celsius, 1),
                                "high": 80.0,  # Estimated safe threshold
                                "critical": 90.0  # Estimated critical threshold
                            })
                            all_temps.append(temp_celsius)
                            
                            temperatures["summary"]["cpu_temp"] = max(
                                temperatures["summary"]["cpu_temp"], temp_celsius
                            )
            except:
                # MSAcpi_ThermalZoneTemperature might not be available
                pass
            
            # Calculate summary statistics
            if all_temps:
                temperatures["summary"]["highest_temp"] = max(all_temps)
                temperatures["summary"]["average_temp"] = round(sum(all_temps) / len(all_temps), 1)
                
                # Check for critical temperatures (estimated thresholds)
                for temp in all_temps:
                    if temp > 85:  # Estimated critical threshold
                        temperatures["summary"]["critical_sensors"].append({
                            "sensor": "System",
                            "label": "High Temperature Detected",
                            "temp": temp,
                            "critical": 85.0
                        })
                        
        except Exception as e:
            print(f"Error getting WMI temperature data: {e}")
        
        return temperatures

    def get_fps_metrics(self) -> Dict:
        """Get FPS metrics (placeholder for now)"""
        # TODO: Implement RTSS shared memory reading or other FPS detection
        return {
            "current_fps": 0,
            "average_fps": 0,
            "source": "not_available"
        }

    def get_system_info(self) -> Dict:
        """Get general system information"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            
            return {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "hostname": platform.node(),
                "uptime_seconds": round(uptime_seconds),
                "boot_time": boot_time
            }
        except Exception as e:
            print(f"Error getting system info: {e}")
            return {}

    def get_network_metrics(self) -> Dict:
        """Get network usage metrics"""
        try:
            network_io = psutil.net_io_counters()
            return {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
                "errin": network_io.errin,
                "errout": network_io.errout,
                "dropin": network_io.dropin,
                "dropout": network_io.dropout
            }
        except Exception as e:
            print(f"Error getting network metrics: {e}")
            return {}

    def _convert_ohm_to_gpu_format(self, load_data: Dict, temp_data: Dict) -> List[Dict]:
        """Convert OpenHardwareMonitor data to GPU format expected by overlay"""
        gpus = []
        
        # Get temperature sensors
        temp_sensors = temp_data.get("sensors", {})
        
        # Look for GPU-related hardware
        gpu_hardware = {}
        for hardware_name, sensors in temp_sensors.items():
            hardware_lower = hardware_name.lower()
            if any(keyword in hardware_lower for keyword in ["gpu", "graphics", "video", "nvidia", "amd", "radeon", "geforce"]):
                gpu_hardware[hardware_name] = {
                    "temp_sensors": sensors,
                    "load_sensors": []
                }
        
        # Add load data for GPU hardware
        for load_name, load_info in load_data.items():
            hardware_name = load_info.get("hardware", "")
            if hardware_name in gpu_hardware:
                gpu_hardware[hardware_name]["load_sensors"].append(load_info)
        
        # Convert to expected format
        for hardware_name, gpu_info in gpu_hardware.items():
            # Find highest temperature
            max_temp = 0
            for temp_sensor in gpu_info["temp_sensors"]:
                max_temp = max(max_temp, temp_sensor.get("current", 0))
            
            # Find GPU load
            gpu_load = 0
            for load_sensor in gpu_info["load_sensors"]:
                sensor_name = load_sensor.get("sensor", "").lower()
                if "gpu" in sensor_name or "core" in sensor_name:
                    gpu_load = max(gpu_load, load_sensor.get("value", 0))
            
            # Determine vendor
            name_lower = hardware_name.lower()
            if "nvidia" in name_lower or "geforce" in name_lower:
                vendor = "NVIDIA"
            elif "amd" in name_lower or "radeon" in name_lower:
                vendor = "AMD"
            elif "intel" in name_lower:
                vendor = "Intel"
            else:
                vendor = "Unknown"
            
            gpu_data = {
                "vendor": vendor,
                "name": hardware_name,
                "memory_total": 0,  # Not available from OHM easily
                "memory_total_mb": 0,
                "utilization_gpu": int(gpu_load),
                "utilization_memory": 0,
                "temperature": int(max_temp)
            }
            
            gpus.append(gpu_data)
        
        return gpus

    def get_gpu_metrics_via_powershell(self) -> List[Dict]:
        """Get GPU metrics using PowerShell performance counters (similar to Task Manager)"""
        gpus = []
        
        try:
            # Simplified PowerShell command for better performance
            ps_command = '''
            $m=0;$n="GPU";try{(Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -EA Stop).CounterSamples|%{if($_.CookedValue -gt $m){$m=$_.CookedValue}};$g=(Get-CimInstance Win32_VideoController|?{$_.Name -notmatch "Microsoft"}|select -f 1).Name;if($g){$n=$g}}catch{};echo "$m|$n"
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=3,  # Reduced timeout
                creationflags=subprocess.CREATE_NO_WINDOW  # Hide window
            )
            
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                parts = output.split('|')
                
                if len(parts) >= 2:
                    try:
                        max_util = float(parts[0])
                        gpu_name = parts[1] if len(parts) > 1 else "Unknown GPU"
                        
                        # Only return if we have meaningful utilization data
                        if max_util >= 0 and gpu_name != "GPU":  # Exclude default fallback
                            vendor = ("NVIDIA" if "nvidia" in gpu_name.lower() or "geforce" in gpu_name.lower()
                                    else "AMD" if "amd" in gpu_name.lower() or "radeon" in gpu_name.lower()
                                    else "Intel" if "intel" in gpu_name.lower()
                                    else "Unknown")
                            
                            gpus.append({
                                "vendor": vendor,
                                "name": gpu_name,
                                "utilization_gpu": int(round(max_util)),
                                "utilization_memory": 0,
                                "temperature": 0,  # Will be filled from OHM if available
                                "memory_total": 0,
                                "memory_total_mb": 0,
                                "memory_used": 0,
                                "memory_used_mb": 0,
                                "source": "powershell"
                            })
                            
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing PowerShell GPU output '{output}': {e}")
                        
        except subprocess.TimeoutExpired:
            # PowerShell method timed out - this is expected in some environments
            pass
        except Exception as e:
            print(f"Error getting PowerShell GPU metrics: {e}")
        
        return gpus
