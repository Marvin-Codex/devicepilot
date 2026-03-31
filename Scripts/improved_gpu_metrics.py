"""
Improved GPU Metrics Collection - Fixes for common issues
This module provides enhanced GPU monitoring with better accuracy and error handling
"""

import subprocess
import time
import json
from typing import Dict, List, Optional, Tuple
import platform

class ImprovedGPUMetrics:
    """Enhanced GPU metrics collection with better accuracy"""
    
    def __init__(self):
        self.last_utilization_reading = 0
        self.last_reading_time = 0
        self.cached_gpu_info = None
        self.cache_timeout = 5  # Cache GPU info for 5 seconds
        
    def get_accurate_gpu_utilization(self) -> float:
        """Get GPU utilization using the most accurate method available"""
        
        # Method 1: PowerShell with improved accuracy (similar to Task Manager)
        utilization = self._get_powershell_gpu_utilization()
        if utilization is not None:
            return utilization
            
        # Fallback: Return last known value or 0
        return self.last_utilization_reading
    
    def _get_powershell_gpu_utilization(self) -> Optional[float]:
        """Get GPU utilization using PowerShell with improved command"""
        try:
            # Enhanced PowerShell command that's more reliable
            ps_command = '''
            $ErrorActionPreference = "SilentlyContinue"
            try {
                # Get GPU Engine counters with error handling
                $counters = Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -ErrorAction Stop
                $maxUtil = 0
                $validReadings = 0
                
                # Process each counter sample
                foreach ($sample in $counters.CounterSamples) {
                    $value = $sample.CookedValue
                    if ($value -ge 0 -and $value -le 100) {
                        $validReadings++
                        if ($value -gt $maxUtil) {
                            $maxUtil = $value
                        }
                    }
                }
                
                # Only return result if we have valid readings
                if ($validReadings -gt 0) {
                    [Math]::Round($maxUtil, 2)
                } else {
                    "NO_VALID_READINGS"
                }
            } catch {
                "ERROR: $($_.Exception.Message)"
            }
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=8,  # Increased timeout
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                
                # Handle error cases
                if output.startswith("ERROR:"):
                    print(f"PowerShell GPU error: {output[7:]}")
                    return None
                elif output == "NO_VALID_READINGS":
                    print("No valid GPU utilization readings available")
                    return 0.0
                
                # Try to parse as float
                try:
                    utilization = float(output)
                    if 0 <= utilization <= 100:
                        self.last_utilization_reading = utilization
                        self.last_reading_time = time.time()
                        return utilization
                    else:
                        print(f"GPU utilization out of range: {utilization}%")
                        return None
                except ValueError:
                    print(f"Cannot parse GPU utilization: '{output}'")
                    return None
            else:
                print(f"PowerShell command failed: {result.stderr.strip()}")
                return None
                
        except subprocess.TimeoutExpired:
            print("GPU utilization query timed out")
            return None
        except Exception as e:
            print(f"Error getting GPU utilization: {e}")
            return None
    
    def get_gpu_info(self) -> Dict:
        """Get comprehensive GPU information with caching"""
        current_time = time.time()
        
        # Use cached info if recent
        if (self.cached_gpu_info and 
            current_time - self.last_reading_time < self.cache_timeout):
            return self.cached_gpu_info
        
        gpu_info = self._collect_gpu_info()
        
        if gpu_info:
            self.cached_gpu_info = gpu_info
            self.last_reading_time = current_time
        
        return gpu_info or {}
    
    def _collect_gpu_info(self) -> Optional[Dict]:
        """Collect comprehensive GPU information"""
        try:
            # Enhanced PowerShell command for GPU info
            ps_command = '''
            $ErrorActionPreference = "SilentlyContinue"
            
            # Get GPU utilization
            $maxUtil = 0
            try {
                $counters = Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -ErrorAction Stop
                foreach ($sample in $counters.CounterSamples) {
                    $value = $sample.CookedValue
                    if ($value -gt $maxUtil -and $value -le 100) {
                        $maxUtil = $value
                    }
                }
            } catch {
                $maxUtil = -1  # Indicate error
            }
            
            # Get GPU hardware info
            $gpu = Get-CimInstance Win32_VideoController | Where-Object {
                $_.Name -notmatch "Microsoft" -and 
                $_.PNPDeviceID -notmatch "ROOT" -and
                $_.VideoArchitecture -ne $null
            } | Select-Object -First 1
            
            if ($gpu) {
                $name = $gpu.Name
                $memory = [Math]::Round($gpu.AdapterRAM / 1MB, 0)
                $driver = $gpu.DriverVersion
                $status = $gpu.Status
            } else {
                $name = "Unknown GPU"
                $memory = 0
                $driver = "Unknown"
                $status = "Unknown"
            }
            
            # Output as JSON-like format for easier parsing
            @{
                utilization = $maxUtil
                name = $name
                memory_mb = $memory
                driver_version = $driver
                status = $status
                timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
            } | ConvertTo-Json -Compress
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    # Parse JSON output
                    gpu_data = json.loads(result.stdout.strip())
                    
                    # Validate and clean data
                    utilization = gpu_data.get('utilization', -1)
                    if utilization < 0:
                        utilization = 0  # Set to 0 if error occurred
                    
                    return {
                        'vendor': self._determine_vendor(gpu_data.get('name', '')),
                        'name': gpu_data.get('name', 'Unknown GPU'),
                        'utilization_gpu': float(utilization),
                        'memory_total_mb': int(gpu_data.get('memory_mb', 0)),
                        'driver_version': gpu_data.get('driver_version', 'Unknown'),
                        'status': gpu_data.get('status', 'Unknown'),
                        'timestamp': gpu_data.get('timestamp', ''),
                        'source': 'powershell_enhanced'
                    }
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"Error parsing GPU info JSON: {e}")
                    print(f"Raw output: {result.stdout[:200]}...")
                    return None
            else:
                print(f"Failed to get GPU info: {result.stderr.strip()}")
                return None
                
        except Exception as e:
            print(f"Error collecting GPU info: {e}")
            return None
    
    def _determine_vendor(self, gpu_name: str) -> str:
        """Determine GPU vendor from name"""
        name_lower = gpu_name.lower()
        
        if any(keyword in name_lower for keyword in ["nvidia", "geforce", "gtx", "rtx", "quadro", "tesla"]):
            return "NVIDIA"
        elif any(keyword in name_lower for keyword in ["amd", "radeon", "rx", "vega", "navi"]):
            return "AMD"
        elif any(keyword in name_lower for keyword in ["intel", "uhd", "iris", "hd graphics", "arc", "xe"]):
            return "Intel"
        else:
            return "Unknown"
    
    def get_multiple_readings(self, count: int = 3, interval: float = 0.5) -> List[float]:
        """Get multiple utilization readings for better accuracy"""
        readings = []
        
        for i in range(count):
            if i > 0:
                time.sleep(interval)
            
            utilization = self.get_accurate_gpu_utilization()
            if utilization is not None:
                readings.append(utilization)
        
        return readings
    
    def get_stable_utilization(self) -> Tuple[float, float]:
        """Get stable GPU utilization with confidence measure"""
        readings = self.get_multiple_readings(count=5, interval=0.3)
        
        if not readings:
            return 0.0, 0.0
        
        # Calculate average and standard deviation
        avg_util = sum(readings) / len(readings)
        
        if len(readings) > 1:
            variance = sum((x - avg_util) ** 2 for x in readings) / (len(readings) - 1)
            std_dev = variance ** 0.5
            confidence = max(0, 100 - std_dev)  # Lower std dev = higher confidence
        else:
            confidence = 50.0
        
        return avg_util, confidence

def test_improved_gpu_metrics():
    """Test the improved GPU metrics"""
    print("=== Testing Improved GPU Metrics ===")
    
    gpu_metrics = ImprovedGPUMetrics()
    
    # Test 1: Basic utilization
    print("\n1. Testing basic GPU utilization...")
    util = gpu_metrics.get_accurate_gpu_utilization()
    if util is not None:
        print(f"   Current GPU utilization: {util:.1f}%")
    else:
        print("   Failed to get GPU utilization")
    
    # Test 2: Comprehensive info
    print("\n2. Testing comprehensive GPU info...")
    info = gpu_metrics.get_gpu_info()
    if info:
        print(f"   GPU: {info.get('name', 'Unknown')}")
        print(f"   Vendor: {info.get('vendor', 'Unknown')}")
        print(f"   Utilization: {info.get('utilization_gpu', 0):.1f}%")
        print(f"   Memory: {info.get('memory_total_mb', 0)} MB")
        print(f"   Driver: {info.get('driver_version', 'Unknown')}")
    else:
        print("   Failed to get GPU info")
    
    # Test 3: Multiple readings
    print("\n3. Testing multiple readings for accuracy...")
    readings = gpu_metrics.get_multiple_readings(count=3)
    if readings:
        print(f"   Readings: {[f'{r:.1f}%' for r in readings]}")
        print(f"   Average: {sum(readings)/len(readings):.1f}%")
        print(f"   Range: {max(readings) - min(readings):.1f}%")
    else:
        print("   Failed to get multiple readings")
    
    # Test 4: Stable utilization
    print("\n4. Testing stable utilization measurement...")
    stable_util, confidence = gpu_metrics.get_stable_utilization()
    print(f"   Stable utilization: {stable_util:.1f}%")
    print(f"   Confidence: {confidence:.1f}%")
    
    return gpu_metrics

if __name__ == "__main__":
    metrics = test_improved_gpu_metrics()
    
    print("\n=== Summary ===")
    print("This improved GPU metrics implementation provides:")
    print("• Better error handling and timeout management")
    print("• More accurate PowerShell commands")
    print("• Multiple readings for stability")
    print("• Caching to reduce performance impact")
    print("• Confidence measurements")
    print("\nIntegrate this into your main metrics collector for better GPU monitoring.")
