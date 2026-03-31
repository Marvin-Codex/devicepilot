#!/usr/bin/env python3
"""
DevicePilot - Professional System Monitoring Overlay
Main application entry point with system tray integration
"""

import sys
import os
import threading
import time
import json
from pathlib import Path
from PyQt6 import QtWidgets, QtCore, QtGui
from devicepilot.ui.overlay_window import OverlayWindow
from devicepilot.ui.settings_window import SettingsWindow
from devicepilot.ui.battery_window import BatteryWindow
from devicepilot.ui.temperature_window import TemperatureWindow
from devicepilot.core.metrics import MetricsCollector
from devicepilot.core.profiles import ProfileManager
from devicepilot.settings.config_manager import ConfigManager


class DevicePilotApp(QtWidgets.QApplication):
    # Signal to communicate from background thread to main thread
    metrics_updated = QtCore.pyqtSignal(dict, bool)
    
    def __init__(self):
        super().__init__(sys.argv)
        
        # Set application properties
        self.setApplicationName("DevicePilot")
        self.setApplicationVersion("1.0.0")
        self.setApplicationDisplayName("DevicePilot - System Monitor")
        self.setQuitOnLastWindowClosed(False)
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.metrics_collector = MetricsCollector()
        self.profile_manager = ProfileManager(self.config_manager)
        
        # Initialize windows
        self.overlay_window = OverlayWindow(self.config_manager)
        self.overlay_window.set_main_app(self)  # Set reference for double-click handlers
        self.settings_window = None
        self.battery_window = None
        self.temperature_window = None
        
        # System tray
        self.setup_system_tray()
        
        # Metrics update thread
        self.metrics_thread = None
        self.running = False
        
        # Connect signals
        self.setup_connections()
        
        # Start monitoring
        self.start_monitoring()
        
        # Show overlay on startup
        self.show_overlay_on_startup()

    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            QtWidgets.QMessageBox.critical(
                None, "DevicePilot",
                "System tray is not available on this system."
            )
            sys.exit(1)
        
        # Create tray icon
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        
        # Set icon (using a default icon for now)
        icon = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)
        
        # Create context menu
        tray_menu = QtWidgets.QMenu()
        
        # Show/Hide Overlay
        toggle_action = tray_menu.addAction("Toggle Overlay")
        toggle_action.triggered.connect(self.toggle_overlay)
        
        # Click-through toggle
        clickthrough_action = tray_menu.addAction("Toggle Click-through")
        clickthrough_action.triggered.connect(self.toggle_click_through)
        
        tray_menu.addSeparator()
        
        # Settings
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        
        # Battery Health
        battery_action = tray_menu.addAction("Battery Health")
        battery_action.triggered.connect(self.show_battery_health)
        
        # Temperature Monitor
        temp_action = tray_menu.addAction("Temperature Monitor")
        temp_action.triggered.connect(self.show_temperature_monitor)
        
        tray_menu.addSeparator()
        
        # Quit
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Tray icon activation
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def setup_connections(self):
        """Setup signal connections between components"""
        # Connect configuration changes to overlay updates
        self.config_manager.config_changed.connect(self.overlay_window.update_config)
        
        # Connect metrics signal to overlay update (main thread)
        self.metrics_updated.connect(self.overlay_window.update_metrics)

    def start_monitoring(self):
        """Start the metrics monitoring thread"""
        self.running = True
        self.metrics_thread = threading.Thread(target=self.metrics_loop, daemon=True)
        self.metrics_thread.start()

    def metrics_loop(self):
        """Main metrics collection and update loop"""
        while self.running:
            try:
                # Collect system metrics
                metrics = self.metrics_collector.get_all_metrics()
                
                # Check for active processes (games)
                active_processes = self.profile_manager.get_active_processes()
                is_gaming = len(active_processes) > 0
                
                # Emit signal to update overlay on main thread
                self.metrics_updated.emit(metrics, is_gaming)
                
                # Sleep based on update interval
                update_interval = self.config_manager.get_setting('metrics.update_interval', 2.0)
                time.sleep(update_interval)
                
            except Exception as e:
                print(f"Error in metrics loop: {e}")
                time.sleep(1.0)

    def toggle_overlay(self):
        """Toggle overlay visibility"""
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
            print("Overlay hidden")
        else:
            self.overlay_window.show()
            print("Overlay shown")

    def toggle_click_through(self):
        """Toggle click-through mode"""
        self.overlay_window.toggle_click_through()

    def show_settings(self):
        """Show settings window"""
        if self.settings_window is None:
            self.settings_window = SettingsWindow(self.config_manager, self.profile_manager)
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()

    def show_battery_health(self):
        """Show battery health window"""
        if self.battery_window is None:
            self.battery_window = BatteryWindow()
        
        self.battery_window.show()
        self.battery_window.raise_()
        self.battery_window.activateWindow()

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_overlay()

    def show_overlay_on_startup(self):
        """Show overlay on application startup based on configuration"""
        startup_config = self.config_manager.get_section("startup")
        overlay_config = self.config_manager.get_section("overlay")
        
        # Check if overlay should be visible on startup
        show_on_startup = overlay_config.get("visible", True)
        start_minimized = startup_config.get("start_minimized", True)
        
        if show_on_startup and not start_minimized:
            self.overlay_window.show()
            print("DevicePilot overlay started")
        elif show_on_startup:
            # Show overlay even if starting minimized, as it's a floating overlay
            self.overlay_window.show()
            print("DevicePilot overlay started (minimized mode)")
        else:
            self.overlay_window.hide()
            print("DevicePilot overlay hidden on startup")
        
        # Show a brief system tray notification
        if self.tray_icon.supportsMessages():
            message = "DevicePilot is running! Right-click the tray icon for options."
            self.tray_icon.showMessage(
                "DevicePilot Started",
                message,
                QtWidgets.QSystemTrayIcon.MessageIcon.Information,
                3000  # 3 seconds
            )

    def show_temperature_monitor(self):
        """Show temperature monitoring window"""
        if self.temperature_window is None:
            self.temperature_window = TemperatureWindow(self.metrics_collector)
        self.temperature_window.show_window()

    def quit_application(self):
        """Clean shutdown of the application"""
        self.running = False
        if self.metrics_thread and self.metrics_thread.is_alive():
            self.metrics_thread.join(timeout=2.0)
        
        self.tray_icon.hide()
        self.quit()


def main():
    """Main entry point"""
    # Enable high DPI scaling (not needed in PyQt6 as it's enabled by default)
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
    # QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    
    app = DevicePilotApp()
    
    # The welcome message is now shown in show_overlay_on_startup()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
