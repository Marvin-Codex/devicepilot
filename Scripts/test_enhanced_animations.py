#!/usr/bin/env python3
"""
Test enhanced animations for metric widgets
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt6 import QtWidgets, QtCore
from devicepilot.settings.config_manager import ConfigManager
from devicepilot.ui.overlay_window import OverlayWindow

class AnimationTestApp(QtWidgets.QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        
        # Initialize components
        self.config_manager = ConfigManager()
        
        # Create overlay window
        self.overlay = OverlayWindow(self.config_manager)
        self.overlay.show()
        
        # Timer to simulate metrics updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.simulate_metrics)
        self.timer.start(3000)  # Update every 3 seconds
        
        self.test_cycle = 0
        print("Enhanced animation test started...")
        print("Watch the widgets animate with improved effects:")
        print("- Smoother value transitions")
        print("- Color transitions")
        print("- Pulse effects on significant changes")
        print("- Subtle breathing animation")
    
    def simulate_metrics(self):
        """Simulate changing metrics with various scenarios"""
        scenarios = [
            {  # High usage scenario
                "cpu": {"usage_percent": 85.0},
                "memory": {"percentage": 75.0},
                "gpu": [{"utilization_gpu": 90.0}],
                "temperature": {"coretemp": [{"current": 68.0}]},
                "battery": {"percentage": 45.0, "plugged": False, "status": "Discharging"},
                "fps": {"current_fps": 120}
            },
            {  # Low usage scenario
                "cpu": {"usage_percent": 15.0},
                "memory": {"percentage": 35.0},
                "gpu": [{"utilization_gpu": 5.0}],
                "temperature": {"coretemp": [{"current": 42.0}]},
                "battery": {"percentage": 85.0, "plugged": True, "status": "Charging"},
                "fps": {"current_fps": 60}
            },
            {  # Critical battery scenario
                "cpu": {"usage_percent": 25.0},
                "memory": {"percentage": 50.0},
                "gpu": [{"utilization_gpu": 10.0}],
                "temperature": {"coretemp": [{"current": 45.0}]},
                "battery": {"percentage": 15.0, "plugged": False, "status": "Critical"},
                "fps": {"current_fps": 30}
            },
            {  # Gaming scenario
                "cpu": {"usage_percent": 95.0},
                "memory": {"percentage": 88.0},
                "gpu": [{"utilization_gpu": 98.0}],
                "temperature": {"coretemp": [{"current": 82.0}]},
                "battery": {"percentage": 100.0, "plugged": True, "status": "Full"},
                "fps": {"current_fps": 144}
            }
        ]
        
        metrics = scenarios[self.test_cycle % len(scenarios)]
        scenario_names = ["High Usage", "Low Usage", "Critical Battery", "Gaming"]
        
        print(f"\nTesting scenario: {scenario_names[self.test_cycle % len(scenarios)]}")
        print(f"Battery: {metrics['battery']['percentage']}%, {metrics['battery']['status']}")
        
        # Update overlay
        is_gaming = self.test_cycle % len(scenarios) == 3
        self.overlay.update_metrics(metrics, is_gaming)
        
        self.test_cycle += 1

if __name__ == "__main__":
    app = AnimationTestApp()
    sys.exit(app.exec())
