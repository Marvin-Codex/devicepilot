#!/usr/bin/env python3
"""
GPU Metrics Fix - Addresses common issues with GPU monitoring
"""

import sys
import os
import time
import json
import subprocess
import platform
from typing import Dict, List, Optional

# Add devicepilot to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'devicepilot'))

def test_powershell_gpu_direct():
    """Test PowerShell GPU metrics directly with improved error handling"""
    print("=== Direct PowerShell GPU Test ===")
    
    try:
        # Improved PowerShell command with better error handling and timeout
        ps_command = '''
        try {
            $ErrorActionPreference = "Stop"
            $counters = Get-Counter "\\GPU Engine(*)\\Utilization Percentage" -ErrorAction Stop
            $maxUtil = 0
            $counters.CounterSamples | ForEach-Object {
                if ($_.CookedValue -gt $maxUtil) {
                    $maxUtil = $_.CookedValue
                }
            }
            $gpu = (Get-CimInstance Win32_VideoController | Where-Object {$_.Name -notmatch "Microsoft" -and $_.PNPDeviceID -notmatch "ROOT"} | Select-Object -First 1).Name
            if (-not $gpu) { $gpu = "Unknown GPU" }
            Write-Output "$maxUtil|$gpu"
        } catch {
            Write-Output "ERROR|$($_.Exception.Message)"
        }
        '''
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: '{result.stdout.strip()}'")
        print(f"STDERR: '{result.stderr.strip()}'")
        
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            if output.startswith("ERROR|"):
                print(f"PowerShell error: {output[6:]}")
                return None
            
            parts = output.split('|')
            if len(parts) >= 2:
                try:
                    utilization = float(parts[0])
                    gpu_name = parts[1]
                    print(f"✓ GPU found: {gpu_name} at {utilization}% utilization")
                    return {"utilization": utilization, "name": gpu_name}
                except ValueError as e:
                    print(f"Error parsing output: {e}")
        else:
            print("PowerShell command failed or returned no output")
            
    except subprocess.TimeoutExpired:
        print("PowerShell command timed out")
    except Exception as e:
        print(f"Error running PowerShell command: {e}")
    
    return None

def test_alternative_gpu_detection():
    """Test alternative GPU detection methods"""
    print("\n=== Alternative GPU Detection Methods ===")
    
    # Method 1: WMI with different approach
    print("\n1. Testing WMI GPU Detection...")
    try:
        import wmi
        c = wmi.WMI()
        
        # Get video controllers
        gpus = c.Win32_VideoController()
        print(f"Found {len(gpus)} video controllers:")
        
        for i, gpu in enumerate(gpus):
            name = getattr(gpu, 'Name', 'Unknown')
            pnp_id = getattr(gpu, 'PNPDeviceID', '')
            status = getattr(gpu, 'Status', 'Unknown')
            
            # Filter out virtual/software GPUs
            if 'Microsoft' not in name and 'ROOT\\' not in pnp_id:
                print(f"  GPU {i}: {name} (Status: {status})")
                
                # Try to get performance data
                try:
                    # This is a simplified approach - real implementation would need performance counters
                    print(f"    PNP Device ID: {pnp_id}")
                except Exception as e:
                    print(f"    Error getting performance data: {e}")
    except ImportError:
        print("WMI not available (pip install wmi)")
    except Exception as e:
        print(f"WMI error: {e}")
    
    # Method 2: Direct performance counter access
    print("\n2. Testing Direct Performance Counters...")
    try:
        ps_counters_cmd = '''
        Get-Counter "\\GPU Engine(*)\\Utilization Percentage" | ForEach-Object {
            $_.CounterSamples | ForEach-Object {
                Write-Output "$($_.Path): $($_.CookedValue)%"
            }
        }
        '''
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_counters_cmd],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            print(f"Found {len(lines)} GPU engine counters:")
            for line in lines[:10]:  # Show first 10
                if line.strip():
                    print(f"  {line.strip()}")
        else:
            print(f"Failed to get performance counters: {result.stderr}")
            
    except Exception as e:
        print(f"Error accessing performance counters: {e}")

def test_ohm_dll_issues():
    """Test OpenHardwareMonitor DLL issues"""
    print("\n=== OpenHardwareMonitor DLL Test ===")
    
    # Check if DLL exists
    ohm_dll_path = os.path.join(os.path.dirname(__file__), 'devicepilot', 'libs', 'OpenHardwareMonitorLib.dll')
    print(f"Checking for DLL at: {ohm_dll_path}")
    
    if os.path.exists(ohm_dll_path):
        print("✓ DLL file exists")
        print(f"  Size: {os.path.getsize(ohm_dll_path)} bytes")
        
        # Test pythonnet import
        try:
            import clr
            print("✓ pythonnet (clr) imported successfully")
            
            # Try to load the DLL
            try:
                clr.AddReference(str(ohm_dll_path))
                print("✓ DLL loaded successfully")
                
                # Try to import OpenHardwareMonitor namespace
                try:
                    from OpenHardwareMonitor import Hardware
                    print("✓ OpenHardwareMonitor namespace imported")
                    
                    # Try to create Computer instance
                    try:
                        computer = Hardware.Computer()
                        computer.GPUEnabled = True
                        computer.Open()
                        print("✓ OpenHardwareMonitor Computer initialized")
                        
                        # Check for hardware
                        hardware_count = len(list(computer.Hardware))
                        print(f"  Found {hardware_count} hardware devices")
                        
                        computer.Close()
                        
                    except Exception as e:
                        print(f"✗ Failed to initialize Computer: {e}")
                        
                except Exception as e:
                    print(f"✗ Failed to import OpenHardwareMonitor namespace: {e}")
                    
            except Exception as e:
                print(f"✗ Failed to load DLL: {e}")
                
        except ImportError:
            print("✗ pythonnet not installed (pip install pythonnet)")
            
    else:
        print("✗ DLL file not found")
        print("  Download from: https://github.com/openhardwaremonitor/openhardwaremonitor")

def check_gpu_utilization_accuracy():
    """Check GPU utilization reporting accuracy"""
    print("\n=== GPU Utilization Accuracy Check ===")
    
    # Compare with Task Manager approach
    print("Comparing different utilization measurement approaches...")
    
    # Method 1: Get all GPU engine utilizations
    ps_cmd = '''
    $engines = Get-Counter "\\GPU Engine(*)\\Utilization Percentage"
    $total = 0
    $count = 0
    $max = 0
    $engines.CounterSamples | ForEach-Object {
        $val = $_.CookedValue
        $total += $val
        $count++
        if ($val -gt $max) { $max = $val }
    }
    $avg = if ($count -gt 0) { $total / $count } else { 0 }
    Write-Output "MAX:$max|AVG:$avg|COUNT:$count"
    '''
    
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            if "MAX:" in output:
                parts = output.split('|')
                max_util = parts[0].split(':')[1]
                avg_util = parts[1].split(':')[1]
                engine_count = parts[2].split(':')[1]
                
                print(f"  GPU Engines found: {engine_count}")
                print(f"  Maximum utilization: {max_util}%")
                print(f"  Average utilization: {avg_util}%")
                print(f"  Recommendation: Use MAX value for gaming scenarios")
                
    except Exception as e:
        print(f"Error testing utilization accuracy: {e}")

def suggest_fixes():
    """Suggest fixes for common GPU metrics issues"""
    print("\n=== Suggested Fixes ===")
    
    fixes = [
        "1. GPU Utilization Issues:",
        "   • Use PowerShell performance counters (most accurate)",
        "   • Take maximum value from all GPU engines",
        "   • Ensure GPU performance counters are enabled in Windows",
        "",
        "2. Temperature Reading Issues:",
        "   • Install OpenHardwareMonitor service",
        "   • Run application as administrator",
        "   • Check if GPU supports temperature sensors",
        "",
        "3. Memory Usage Issues:",
        "   • Use NVML for NVIDIA GPUs (most accurate)",
        "   • Fallback to WMI for memory information",
        "   • Parse GPU engine names for memory controller data",
        "",
        "4. Performance Issues:",
        "   • Reduce polling frequency (avoid polling faster than 1Hz)",
        "   • Cache results and update asynchronously",
        "   • Use timeout on PowerShell commands",
        "",
        "5. Compatibility Issues:",
        "   • Test on different GPU vendors (NVIDIA, AMD, Intel)",
        "   • Handle cases where no discrete GPU exists",
        "   • Graceful fallback when services are unavailable"
    ]
    
    for fix in fixes:
        print(fix)

def main():
    """Main test execution"""
    print("=== GPU Metrics Diagnostic Tool ===")
    print("This tool helps identify and fix GPU metrics issues\n")
    
    # Test 1: Direct PowerShell
    gpu_data = test_powershell_gpu_direct()
    
    # Test 2: Alternative methods
    test_alternative_gpu_detection()
    
    # Test 3: OHM DLL issues
    test_ohm_dll_issues()
    
    # Test 4: Utilization accuracy
    check_gpu_utilization_accuracy()
    
    # Test 5: Suggest fixes
    suggest_fixes()
    
    print("\n=== Summary ===")
    if gpu_data:
        print(f"✓ Basic GPU detection working: {gpu_data['name']}")
        print(f"  Current utilization: {gpu_data['utilization']:.1f}%")
    else:
        print("✗ GPU detection has issues - check the recommendations above")
    
    print("\nNext steps:")
    print("1. Fix any identified issues")
    print("2. Test with actual gaming workload")
    print("3. Verify metrics match Task Manager")

if __name__ == "__main__":
    main()
