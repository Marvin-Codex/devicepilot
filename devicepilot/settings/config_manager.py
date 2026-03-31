"""
Configuration Manager for DevicePilot
Handles saving/loading settings and configuration changes
"""

import json
import os
from pathlib import Path
from PyQt6 import QtCore


class ConfigManager(QtCore.QObject):
    config_changed = QtCore.pyqtSignal(str, object)  # setting_name, value
    
    def __init__(self):
        super().__init__()
        self.config_file = Path("devicepilot/settings/config.json")
        self.default_config = {
            "overlay": {
                "visible": True,
                "position": {"x": 50, "y": 50},
                "dock_side": "none",  # none, center, left, right, top, bottom, top-left, top-right, bottom-left, bottom-right
                "size": {"width": 400, "height": 120},
                "opacity": 0.9,
                "click_through": False,
                "always_on_top": True
            },
            "theme": {
                "style": "modern_dark",  # modern_dark, modern_light, minimal, gaming
                "background_color": "#1e1e1e",
                "text_color": "#ffffff",
                "accent_color": "#007acc",
                "border_radius": 10,
                "shadow_enabled": True,
                "blur_enabled": False,
                "gradient_enabled": True
            },
            "metrics": {
                "update_interval": 2.0,  # Slower update for better animations
                "show_fps": True,
                "show_cpu": True,
                "show_ram": True,
                "show_gpu": True,
                "show_temperature": True,
                "show_battery": True,
                "cpu_cores_individual": False,
                "temperature_unit": "C"  # C or F
            },
            "profiles": {
                "gaming_mode_enabled": True,
                "gaming_processes": [
                    "*.exe",
                    "steam.exe",
                    "origin.exe",
                    "uplay.exe",
                    "epicgameslauncher.exe",
                    "battle.net.exe"
                ],
                "per_app_settings": {}
            },
            "startup": {
                "start_with_windows": False,
                "start_minimized": True,
                "auto_hide_on_fullscreen": True
            },
            "advanced": {
                "require_admin": False,
                "gpu_vendor_preference": "auto",  # auto, nvidia, amd, intel
                "fps_source": "auto",  # auto, rtss, estimated
                "logging_enabled": False
            }
        }
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_config(self.default_config, loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()

    def save_config(self):
        """Save configuration to file"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _merge_config(self, default, loaded):
        """Recursively merge loaded config with defaults"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get_setting(self, path, default=None):
        """Get a setting value using dot notation (e.g., 'overlay.opacity')"""
        keys = path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_setting(self, path, value):
        """Set a setting value using dot notation"""
        keys = path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save and emit signal
        self.save_config()
        self.config_changed.emit(path, value)

    def get_section(self, section_name):
        """Get an entire configuration section"""
        return self.config.get(section_name, {})

    def set_section(self, section_name, section_data):
        """Set an entire configuration section"""
        self.config[section_name] = section_data
        self.save_config()
        self.config_changed.emit(section_name, section_data)

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save_config()
        self.config_changed.emit("*", self.config)

    def export_config(self, file_path):
        """Export configuration to a file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception:
            return False

    def import_config(self, file_path):
        """Import configuration from a file"""
        try:
            with open(file_path, 'r') as f:
                imported_config = json.load(f)
            
            self.config = self._merge_config(self.default_config, imported_config)
            self.save_config()
            self.config_changed.emit("*", self.config)
            return True
        except Exception:
            return False
