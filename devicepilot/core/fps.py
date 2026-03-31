"""
FPS (Frames Per Second) Monitoring Module
Implements multiple methods for FPS detection including RTSS integration
"""

import time
import struct
import mmap
import ctypes
import os
from typing import Optional, Dict, List
import psutil
from ctypes import wintypes
import json


class RTSSReader:
    """Read FPS data from RivaTuner Statistics Server (RTSS) shared memory"""
    
    def __init__(self):
        self.rtss_available = False
        self.shared_memory = None
        self.rtss_apps = {}
        self._check_rtss_availability()

    def _check_rtss_availability(self):
        """Check if RTSS is running and accessible"""
        try:
            # Check if RTSS process is running
            rtss_processes = [
                "RTSS.exe", 
                "RTSSHooksLoader64.exe", 
                "RTSSHooksLoader32.exe",
                "RivaTuner Statistics Server.exe"
            ]
            
            running_processes = [p.name() for p in psutil.process_iter(['name'])]
            self.rtss_available = any(proc in running_processes for proc in rtss_processes)
            
            if self.rtss_available:
                print("RTSS detected and available for FPS monitoring")
            
        except Exception as e:
            print(f"Error checking RTSS availability: {e}")
            self.rtss_available = False

    def read_fps_data(self) -> Optional[Dict]:
        """Read FPS data from RTSS shared memory"""
        if not self.rtss_available:
            return None
        
        try:
            # RTSS shared memory structure (simplified)
            # This is a placeholder implementation
            # Real implementation would require reverse engineering RTSS shared memory format
            
            # Try to access RTSS shared memory
            # Memory name format: "RTSSSharedMemoryV2_<AppName>"
            # This is a simplified approach
            
            return {
                "fps": 0,  # Placeholder
                "frametime": 0,
                "source": "rtss",
                "available": False
            }
            
        except Exception as e:
            print(f"Error reading RTSS data: {e}")
            return None

    def get_monitored_applications(self) -> List[str]:
        """Get list of applications being monitored by RTSS"""
        if not self.rtss_available:
            return []
        
        # This would return apps currently being monitored by RTSS
        # Placeholder implementation
        return []


class DirectXFPSMonitor:
    """Monitor FPS using DirectX/DXGI methods (requires elevated privileges)"""
    
    def __init__(self):
        self.dxgi_available = False
        self._init_dxgi_monitoring()

    def _init_dxgi_monitoring(self):
        """Initialize DXGI-based FPS monitoring"""
        try:
            # This would require native Windows API calls
            # Placeholder for now
            self.dxgi_available = False
            
        except Exception as e:
            print(f"Error initializing DXGI monitoring: {e}")
            self.dxgi_available = False

    def get_fps(self) -> Optional[float]:
        """Get FPS using DXGI present hooks"""
        if not self.dxgi_available:
            return None
        
        # This would implement DirectX present call hooking
        # Very complex and requires native code
        return None


class ProcessBasedFPSEstimator:
    """Estimate FPS based on GPU usage patterns and process behavior"""
    
    def __init__(self):
        self.frame_history = {}
        self.last_sample_time = {}

    def estimate_fps(self, process_name: str, gpu_usage: float) -> Optional[float]:
        """Estimate FPS based on GPU usage patterns"""
        try:
            current_time = time.time()
            
            # Initialize tracking for new processes
            if process_name not in self.frame_history:
                self.frame_history[process_name] = []
                self.last_sample_time[process_name] = current_time
                return None
            
            time_delta = current_time - self.last_sample_time[process_name]
            if time_delta < 0.1:  # Sample every 100ms minimum
                return None
            
            # Very rough estimation based on GPU usage patterns
            # This is not accurate but provides some indication
            history = self.frame_history[process_name]
            history.append((current_time, gpu_usage))
            
            # Keep only recent samples (last 5 seconds)
            history = [(t, usage) for t, usage in history if current_time - t <= 5.0]
            self.frame_history[process_name] = history
            self.last_sample_time[process_name] = current_time
            
            if len(history) < 10:
                return None
            
            # Calculate average time between high GPU usage spikes
            # This is a very crude approximation
            high_usage_points = [t for t, usage in history if usage > 50]
            
            if len(high_usage_points) < 3:
                return None
            
            # Estimate frame intervals
            intervals = []
            for i in range(1, len(high_usage_points)):
                interval = high_usage_points[i] - high_usage_points[i-1]
                if 0.008 <= interval <= 0.1:  # Reasonable frame time range (10-120 FPS)
                    intervals.append(interval)
            
            if not intervals:
                return None
            
            avg_interval = sum(intervals) / len(intervals)
            estimated_fps = 1.0 / avg_interval
            
            # Clamp to reasonable range
            estimated_fps = max(10, min(240, estimated_fps))
            
            return round(estimated_fps, 1)
            
        except Exception as e:
            print(f"Error estimating FPS for {process_name}: {e}")
            return None


class PerformanceCounterFPS:
    """Use Windows Performance Counters for FPS estimation"""
    
    def __init__(self):
        self.counters_available = False
        self._init_performance_counters()

    def _init_performance_counters(self):
        """Initialize performance counter monitoring"""
        try:
            # Check if performance counters are available
            # This would use Windows Performance Toolkit or WMI
            self.counters_available = False  # Placeholder
            
        except Exception as e:
            print(f"Error initializing performance counters: {e}")

    def get_fps_from_counters(self, process_name: str) -> Optional[float]:
        """Get FPS using Windows performance counters"""
        if not self.counters_available:
            return None
        
        # This would query DirectX/OpenGL performance counters
        # Placeholder implementation
        return None


class FPSMonitor:
    """Main FPS monitoring class that combines multiple detection methods"""
    
    def __init__(self):
        self.rtss_reader = RTSSReader()
        self.directx_monitor = DirectXFPSMonitor()
        self.process_estimator = ProcessBasedFPSEstimator()
        self.perf_counter = PerformanceCounterFPS()
        
        self.current_fps = 0.0
        self.current_frametime = 0.0
        self.fps_source = "none"
        self.target_process = None
        
        # Frame time history for smoothing
        self.fps_history = []
        self.max_history = 30  # Keep 30 samples

    def get_current_fps(self) -> Dict:
        """Get current FPS using best available method"""
        fps_data = {
            "current_fps": 0.0,
            "average_fps": 0.0,
            "min_fps": 0.0,
            "max_fps": 0.0,
            "frametime_ms": 0.0,
            "source": "not_available",
            "target_process": None
        }
        
        detected_fps = None
        
        # Try RTSS first (most accurate for gaming)
        if self.rtss_reader.rtss_available:
            rtss_data = self.rtss_reader.read_fps_data()
            if rtss_data and rtss_data.get("fps", 0) > 0:
                detected_fps = rtss_data["fps"]
                fps_data["source"] = "rtss"
                fps_data["frametime_ms"] = rtss_data.get("frametime", 0)
        
        # Try DirectX monitoring (if available and no RTSS)
        if not detected_fps and self.directx_monitor.dxgi_available:
            dx_fps = self.directx_monitor.get_fps()
            if dx_fps and dx_fps > 0:
                detected_fps = dx_fps
                fps_data["source"] = "directx"
        
        # Try performance counters
        if not detected_fps and self.perf_counter.counters_available and self.target_process:
            counter_fps = self.perf_counter.get_fps_from_counters(self.target_process)
            if counter_fps and counter_fps > 0:
                detected_fps = counter_fps
                fps_data["source"] = "performance_counters"
        
        # Fall back to estimation based on GPU usage
        if not detected_fps and self.target_process:
            # This would need GPU usage data passed in
            estimated_fps = self.process_estimator.estimate_fps(self.target_process, 0)
            if estimated_fps and estimated_fps > 0:
                detected_fps = estimated_fps
                fps_data["source"] = "estimated"
        
        # Update FPS data
        if detected_fps:
            self.current_fps = detected_fps
            fps_data["current_fps"] = detected_fps
            fps_data["frametime_ms"] = round(1000.0 / detected_fps, 2) if detected_fps > 0 else 0
            
            # Add to history for averaging
            self.fps_history.append(detected_fps)
            if len(self.fps_history) > self.max_history:
                self.fps_history.pop(0)
            
            # Calculate statistics
            if self.fps_history:
                fps_data["average_fps"] = round(sum(self.fps_history) / len(self.fps_history), 1)
                fps_data["min_fps"] = round(min(self.fps_history), 1)
                fps_data["max_fps"] = round(max(self.fps_history), 1)
        
        fps_data["target_process"] = self.target_process
        return fps_data

    def set_target_process(self, process_name: str):
        """Set the target process for FPS monitoring"""
        self.target_process = process_name

    def auto_detect_gaming_process(self) -> Optional[str]:
        """Auto-detect the most likely gaming process for FPS monitoring"""
        try:
            # Get processes sorted by GPU usage (if available)
            # For now, look for processes with high CPU/memory usage
            candidates = []
            
            for proc in psutil.process_iter(['name', 'exe', 'memory_info', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    if not pinfo['exe'] or not pinfo['name']:
                        continue
                    
                    memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    cpu_percent = pinfo['cpu_percent'] or 0
                    
                    # Look for processes with significant resource usage
                    if memory_mb > 100 and cpu_percent > 5:  # Basic threshold
                        exe_name = os.path.basename(pinfo['exe'])
                        
                        # Skip obvious system processes
                        if not any(sys_proc in exe_name.lower() for sys_proc in 
                                 ['explorer', 'dwm', 'winlogon', 'services', 'svchost']):
                            candidates.append({
                                'name': exe_name,
                                'memory': memory_mb,
                                'cpu': cpu_percent,
                                'score': memory_mb + (cpu_percent * 10)  # Simple scoring
                            })
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by score and return top candidate
            if candidates:
                candidates.sort(key=lambda x: x['score'], reverse=True)
                return candidates[0]['name']
            
        except Exception as e:
            print(f"Error auto-detecting gaming process: {e}")
        
        return None

    def get_fps_capabilities(self) -> Dict:
        """Get information about available FPS monitoring capabilities"""
        return {
            "rtss_available": self.rtss_reader.rtss_available,
            "directx_available": self.directx_monitor.dxgi_available,
            "performance_counters_available": self.perf_counter.counters_available,
            "estimation_available": True,
            "recommended_method": self._get_recommended_method()
        }

    def _get_recommended_method(self) -> str:
        """Get the recommended FPS monitoring method for current system"""
        if self.rtss_reader.rtss_available:
            return "rtss"
        elif self.directx_monitor.dxgi_available:
            return "directx"
        elif self.perf_counter.counters_available:
            return "performance_counters"
        else:
            return "estimation"

    def reset_history(self):
        """Reset FPS history and statistics"""
        self.fps_history.clear()
        self.current_fps = 0.0
        self.current_frametime = 0.0

    def get_fps_statistics(self) -> Dict:
        """Get detailed FPS statistics"""
        if not self.fps_history:
            return {"available": False}
        
        history = self.fps_history.copy()
        
        return {
            "available": True,
            "sample_count": len(history),
            "current": self.current_fps,
            "average": round(sum(history) / len(history), 2),
            "minimum": round(min(history), 2),
            "maximum": round(max(history), 2),
            "percentile_1": round(sorted(history)[int(len(history) * 0.01)], 2),
            "percentile_5": round(sorted(history)[int(len(history) * 0.05)], 2),
            "percentile_95": round(sorted(history)[int(len(history) * 0.95)], 2),
            "percentile_99": round(sorted(history)[int(len(history) * 0.99)], 2),
            "standard_deviation": round(self._calculate_std_dev(history), 2),
            "source": self.fps_source
        }

    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation of FPS values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
