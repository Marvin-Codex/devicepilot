"""
Profile Manager for Gaming Mode Detection and Per-App Settings
Monitors running processes and manages application-specific configurations
"""

import psutil
import time
import fnmatch
from typing import List, Dict, Optional
import json
from pathlib import Path


class ProfileManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.active_processes = set()
        self.gaming_processes = set()
        self.process_cache = {}
        self.cache_timeout = 5.0  # Cache process list for 5 seconds
        self.last_cache_time = 0

    def get_active_processes(self) -> List[str]:
        """Get list of currently active gaming processes"""
        current_time = time.time()
        
        # Use cache if recent
        if current_time - self.last_cache_time < self.cache_timeout:
            return list(self.gaming_processes)
        
        self.gaming_processes.clear()
        
        try:
            # Get gaming process patterns from config
            gaming_patterns = self.config_manager.get_setting("profiles.gaming_processes", [])
            
            # Get all running processes
            running_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    pinfo = proc.info
                    if pinfo['name']:
                        running_processes.append(pinfo['name'].lower())
                    if pinfo['exe']:
                        exe_name = Path(pinfo['exe']).name.lower()
                        running_processes.append(exe_name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Check for gaming process matches
            for pattern in gaming_patterns:
                pattern_lower = pattern.lower()
                for proc_name in running_processes:
                    if fnmatch.fnmatch(proc_name, pattern_lower):
                        self.gaming_processes.add(proc_name)
            
            self.last_cache_time = current_time
            
        except Exception as e:
            print(f"Error getting active processes: {e}")
        
        return list(self.gaming_processes)

    def is_gaming_mode_active(self) -> bool:
        """Check if gaming mode should be active"""
        if not self.config_manager.get_setting("profiles.gaming_mode_enabled", True):
            return False
        
        active_games = self.get_active_processes()
        return len(active_games) > 0

    def get_process_profile(self, process_name: str) -> Optional[Dict]:
        """Get profile settings for a specific process"""
        per_app_settings = self.config_manager.get_setting("profiles.per_app_settings", {})
        return per_app_settings.get(process_name.lower())

    def save_process_profile(self, process_name: str, profile: Dict):
        """Save profile settings for a specific process"""
        per_app_settings = self.config_manager.get_setting("profiles.per_app_settings", {})
        per_app_settings[process_name.lower()] = profile
        self.config_manager.set_setting("profiles.per_app_settings", per_app_settings)

    def delete_process_profile(self, process_name: str):
        """Delete profile for a specific process"""
        per_app_settings = self.config_manager.get_setting("profiles.per_app_settings", {})
        if process_name.lower() in per_app_settings:
            del per_app_settings[process_name.lower()]
            self.config_manager.set_setting("profiles.per_app_settings", per_app_settings)

    def add_gaming_process(self, process_pattern: str):
        """Add a new gaming process pattern"""
        gaming_processes = self.config_manager.get_setting("profiles.gaming_processes", [])
        if process_pattern not in gaming_processes:
            gaming_processes.append(process_pattern)
            self.config_manager.set_setting("profiles.gaming_processes", gaming_processes)

    def remove_gaming_process(self, process_pattern: str):
        """Remove a gaming process pattern"""
        gaming_processes = self.config_manager.get_setting("profiles.gaming_processes", [])
        if process_pattern in gaming_processes:
            gaming_processes.remove(process_pattern)
            self.config_manager.set_setting("profiles.gaming_processes", gaming_processes)

    def get_running_applications(self) -> List[Dict]:
        """Get detailed list of running applications"""
        applications = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    
                    # Skip system processes
                    if not pinfo['exe'] or not pinfo['name']:
                        continue
                    
                    # Filter out common system processes
                    if any(sys_proc in pinfo['name'].lower() for sys_proc in 
                          ['winlogon', 'csrss', 'wininit', 'services', 'lsass', 'svchost']):
                        continue
                    
                    app_info = {
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'exe_path': pinfo['exe'],
                        'exe_name': Path(pinfo['exe']).name,
                        'memory_mb': round(pinfo['memory_info'].rss / (1024 * 1024), 1),
                        'cpu_percent': pinfo['cpu_percent'] or 0,
                        'is_gaming': False
                    }
                    
                    # Check if it's a gaming application
                    gaming_patterns = self.config_manager.get_setting("profiles.gaming_processes", [])
                    for pattern in gaming_patterns:
                        if (fnmatch.fnmatch(app_info['name'].lower(), pattern.lower()) or
                            fnmatch.fnmatch(app_info['exe_name'].lower(), pattern.lower())):
                            app_info['is_gaming'] = True
                            break
                    
                    applications.append(app_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            print(f"Error getting running applications: {e}")
        
        # Sort by memory usage (descending)
        applications.sort(key=lambda x: x['memory_mb'], reverse=True)
        return applications[:50]  # Limit to top 50

    def detect_potential_games(self) -> List[str]:
        """Detect potential gaming applications that aren't in the gaming list"""
        potential_games = []
        applications = self.get_running_applications()
        
        # Common indicators of gaming applications
        gaming_indicators = [
            'game', 'launcher', 'steam', 'epic', 'origin', 'uplay', 'battle',
            'minecraft', 'unity', 'unreal', 'engine', 'dx', 'opengl', 'vulkan'
        ]
        
        for app in applications:
            if app['is_gaming']:
                continue  # Already marked as gaming
            
            # Check if exe name or path contains gaming indicators
            exe_lower = app['exe_name'].lower()
            path_lower = app['exe_path'].lower()
            
            # High CPU or memory usage might indicate a game
            high_resource_usage = app['cpu_percent'] > 30 or app['memory_mb'] > 500
            
            # Check for gaming-related keywords
            has_gaming_keywords = any(indicator in exe_lower or indicator in path_lower 
                                    for indicator in gaming_indicators)
            
            if has_gaming_keywords or (high_resource_usage and len(exe_lower) > 6):
                potential_games.append(app['exe_name'])
        
        return potential_games

    def create_default_gaming_profile(self) -> Dict:
        """Create a default profile for gaming applications"""
        return {
            "overlay_settings": {
                "show_fps": True,
                "expanded_view": True,
                "opacity": 0.8,
                "position": "top_right"
            },
            "metrics_settings": {
                "update_interval": 0.5,
                "show_detailed_gpu": True,
                "show_frametime": True
            },
            "behavior": {
                "auto_hide_delay": 10,
                "click_through": True,
                "always_on_top": True
            }
        }

    def apply_profile_settings(self, profile: Dict):
        """Apply profile settings temporarily (without saving to main config)"""
        # This would temporarily override current settings
        # Implementation would depend on how the overlay handles dynamic config changes
        pass

    def restore_default_settings(self):
        """Restore default settings after gaming session ends"""
        # This would restore the main configuration settings
        pass

    def get_profile_statistics(self) -> Dict:
        """Get statistics about profile usage"""
        per_app_settings = self.config_manager.get_setting("profiles.per_app_settings", {})
        gaming_processes = self.config_manager.get_setting("profiles.gaming_processes", [])
        
        return {
            "total_profiles": len(per_app_settings),
            "gaming_patterns": len(gaming_processes),
            "active_gaming_processes": len(self.get_active_processes())
        }

    def export_profiles(self, file_path: Path) -> bool:
        """Export all profile settings to a file"""
        try:
            profile_data = {
                "gaming_processes": self.config_manager.get_setting("profiles.gaming_processes", []),
                "per_app_settings": self.config_manager.get_setting("profiles.per_app_settings", {}),
                "gaming_mode_enabled": self.config_manager.get_setting("profiles.gaming_mode_enabled", True),
                "export_timestamp": time.time()
            }
            
            with open(file_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error exporting profiles: {e}")
            return False

    def import_profiles(self, file_path: Path) -> bool:
        """Import profile settings from a file"""
        try:
            with open(file_path, 'r') as f:
                profile_data = json.load(f)
            
            # Validate and import data
            if "gaming_processes" in profile_data:
                self.config_manager.set_setting("profiles.gaming_processes", profile_data["gaming_processes"])
            
            if "per_app_settings" in profile_data:
                self.config_manager.set_setting("profiles.per_app_settings", profile_data["per_app_settings"])
            
            if "gaming_mode_enabled" in profile_data:
                self.config_manager.set_setting("profiles.gaming_mode_enabled", profile_data["gaming_mode_enabled"])
            
            return True
        except Exception as e:
            print(f"Error importing profiles: {e}")
            return False

    def get_process_command_line(self, pid: int) -> str:
        """Get command line arguments for a process"""
        try:
            process = psutil.Process(pid)
            return ' '.join(process.cmdline())
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "N/A"

    def is_fullscreen_application_active(self) -> bool:
        """Check if a fullscreen application is currently active"""
        # This is a placeholder for fullscreen detection
        # Would need platform-specific implementation using Windows API
        try:
            # On Windows, you would use GetForegroundWindow() and check window properties
            # For now, return False as placeholder
            return False
        except Exception:
            return False

    def get_foreground_application(self) -> Optional[str]:
        """Get the name of the currently active/foreground application"""
        # This is a placeholder for foreground app detection
        # Would need platform-specific implementation
        try:
            # Implementation would use Windows API to get foreground window
            # and map it to a process name
            return None
        except Exception:
            return None
