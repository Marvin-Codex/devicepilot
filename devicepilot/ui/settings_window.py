"""
Professional Settings Window with Tabbed Interface
Advanced configuration interface for all DevicePilot settings
"""

from PyQt6 import QtWidgets, QtCore, QtGui
import json
from pathlib import Path


class ModernTabWidget(QtWidgets.QTabWidget):
    """Custom tab widget with modern styling"""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)


class OverlaySettingsTab(QtWidgets.QWidget):
    """Overlay appearance and behavior settings"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        
        # Appearance Group
        appearance_group = QtWidgets.QGroupBox("Appearance")
        appearance_layout = QtWidgets.QFormLayout()
        
        # Opacity slider
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(90)
        self.opacity_label = QtWidgets.QLabel("90%")
        opacity_layout = QtWidgets.QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        
        appearance_layout.addRow("Opacity:", opacity_layout)
        
        # Theme selection
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Modern Dark", "Modern Light", "Minimal", "Gaming"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        # Border radius
        self.radius_spin = QtWidgets.QSpinBox()
        self.radius_spin.setRange(0, 20)
        self.radius_spin.setValue(10)
        self.radius_spin.setSuffix("px")
        appearance_layout.addRow("Border Radius:", self.radius_spin)
        
        # Effects
        self.shadow_check = QtWidgets.QCheckBox("Drop Shadow")
        self.blur_check = QtWidgets.QCheckBox("Background Blur")
        self.gradient_check = QtWidgets.QCheckBox("Gradient Background")
        
        effects_layout = QtWidgets.QHBoxLayout()
        effects_layout.addWidget(self.shadow_check)
        effects_layout.addWidget(self.blur_check)
        effects_layout.addWidget(self.gradient_check)
        appearance_layout.addRow("Effects:", effects_layout)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Behavior Group
        behavior_group = QtWidgets.QGroupBox("Behavior")
        behavior_layout = QtWidgets.QFormLayout()
        
        # Position and docking
        self.dock_combo = QtWidgets.QComboBox()
        self.dock_combo.addItems(["None", "Left", "Right", "Top", "Bottom"])
        behavior_layout.addRow("Dock to:", self.dock_combo)
        
        # Always on top
        self.always_top_check = QtWidgets.QCheckBox("Always on Top")
        self.always_top_check.setChecked(True)
        behavior_layout.addRow("", self.always_top_check)
        
        # Click-through
        self.click_through_check = QtWidgets.QCheckBox("Click-through Mode")
        behavior_layout.addRow("", self.click_through_check)
        
        # Auto-hide
        self.auto_hide_check = QtWidgets.QCheckBox("Auto-hide in Fullscreen")
        behavior_layout.addRow("", self.auto_hide_check)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        """Load settings from config"""
        overlay_config = self.config_manager.get_section("overlay")
        theme_config = self.config_manager.get_section("theme")
        
        self.opacity_slider.setValue(int(overlay_config.get("opacity", 0.9) * 100))
        self.radius_spin.setValue(theme_config.get("border_radius", 10))
        self.shadow_check.setChecked(theme_config.get("shadow_enabled", True))
        self.blur_check.setChecked(theme_config.get("blur_enabled", False))
        self.gradient_check.setChecked(theme_config.get("gradient_enabled", True))
        self.always_top_check.setChecked(overlay_config.get("always_on_top", True))
        self.click_through_check.setChecked(overlay_config.get("click_through", False))

    def save_settings(self):
        """Save settings to config"""
        self.config_manager.set_setting("overlay.opacity", self.opacity_slider.value() / 100.0)
        self.config_manager.set_setting("theme.border_radius", self.radius_spin.value())
        self.config_manager.set_setting("theme.shadow_enabled", self.shadow_check.isChecked())
        self.config_manager.set_setting("theme.blur_enabled", self.blur_check.isChecked())
        self.config_manager.set_setting("theme.gradient_enabled", self.gradient_check.isChecked())
        self.config_manager.set_setting("overlay.always_on_top", self.always_top_check.isChecked())
        self.config_manager.set_setting("overlay.click_through", self.click_through_check.isChecked())


class MetricsSettingsTab(QtWidgets.QWidget):
    """Metrics display and update settings"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        
        # Update Settings Group
        update_group = QtWidgets.QGroupBox("Update Settings")
        update_layout = QtWidgets.QFormLayout()
        
        # Update interval
        self.interval_spin = QtWidgets.QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 10.0)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setValue(1.0)
        self.interval_spin.setSuffix(" sec")
        update_layout.addRow("Update Interval:", self.interval_spin)
        
        update_group.setLayout(update_layout)
        layout.addWidget(update_group)
        
        # Display Settings Group
        display_group = QtWidgets.QGroupBox("Display Settings")
        display_layout = QtWidgets.QFormLayout()
        
        # Metric toggles
        self.show_cpu_check = QtWidgets.QCheckBox("Show CPU Usage")
        self.show_ram_check = QtWidgets.QCheckBox("Show RAM Usage")
        self.show_gpu_check = QtWidgets.QCheckBox("Show GPU Usage")
        self.show_temp_check = QtWidgets.QCheckBox("Show Temperature")
        self.show_battery_check = QtWidgets.QCheckBox("Show Battery")
        self.show_fps_check = QtWidgets.QCheckBox("Show FPS (Gaming Mode)")
        
        display_layout.addRow("", self.show_cpu_check)
        display_layout.addRow("", self.show_ram_check)
        display_layout.addRow("", self.show_gpu_check)
        display_layout.addRow("", self.show_temp_check)
        display_layout.addRow("", self.show_battery_check)
        display_layout.addRow("", self.show_fps_check)
        
        # CPU individual cores
        self.cpu_cores_check = QtWidgets.QCheckBox("Show Individual CPU Cores")
        display_layout.addRow("", self.cpu_cores_check)
        
        # Temperature unit
        self.temp_unit_combo = QtWidgets.QComboBox()
        self.temp_unit_combo.addItems(["Celsius (°C)", "Fahrenheit (°F)"])
        display_layout.addRow("Temperature Unit:", self.temp_unit_combo)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        """Load settings from config"""
        metrics_config = self.config_manager.get_section("metrics")
        
        self.interval_spin.setValue(metrics_config.get("update_interval", 1.0))
        self.show_cpu_check.setChecked(metrics_config.get("show_cpu", True))
        self.show_ram_check.setChecked(metrics_config.get("show_ram", True))
        self.show_gpu_check.setChecked(metrics_config.get("show_gpu", True))
        self.show_temp_check.setChecked(metrics_config.get("show_temperature", True))
        self.show_battery_check.setChecked(metrics_config.get("show_battery", True))
        self.show_fps_check.setChecked(metrics_config.get("show_fps", True))
        self.cpu_cores_check.setChecked(metrics_config.get("cpu_cores_individual", False))
        
        temp_unit = metrics_config.get("temperature_unit", "C")
        self.temp_unit_combo.setCurrentIndex(0 if temp_unit == "C" else 1)

    def save_settings(self):
        """Save settings to config"""
        self.config_manager.set_setting("metrics.update_interval", self.interval_spin.value())
        self.config_manager.set_setting("metrics.show_cpu", self.show_cpu_check.isChecked())
        self.config_manager.set_setting("metrics.show_ram", self.show_ram_check.isChecked())
        self.config_manager.set_setting("metrics.show_gpu", self.show_gpu_check.isChecked())
        self.config_manager.set_setting("metrics.show_temperature", self.show_temp_check.isChecked())
        self.config_manager.set_setting("metrics.show_battery", self.show_battery_check.isChecked())
        self.config_manager.set_setting("metrics.show_fps", self.show_fps_check.isChecked())
        self.config_manager.set_setting("metrics.cpu_cores_individual", self.cpu_cores_check.isChecked())
        
        temp_unit = "C" if self.temp_unit_combo.currentIndex() == 0 else "F"
        self.config_manager.set_setting("metrics.temperature_unit", temp_unit)


class GamingSettingsTab(QtWidgets.QWidget):
    """Gaming mode and process detection settings"""
    
    def __init__(self, config_manager, profile_manager):
        super().__init__()
        self.config_manager = config_manager
        self.profile_manager = profile_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        
        # Gaming Mode Group
        gaming_group = QtWidgets.QGroupBox("Gaming Mode")
        gaming_layout = QtWidgets.QVBoxLayout()
        
        self.gaming_enabled_check = QtWidgets.QCheckBox("Enable Gaming Mode Detection")
        gaming_layout.addWidget(self.gaming_enabled_check)
        
        help_label = QtWidgets.QLabel(
            "Gaming mode automatically expands the overlay to show FPS and additional metrics\n"
            "when gaming applications are detected."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #888888; font-style: italic;")
        gaming_layout.addWidget(help_label)
        
        gaming_group.setLayout(gaming_layout)
        layout.addWidget(gaming_group)
        
        # Process Detection Group
        processes_group = QtWidgets.QGroupBox("Gaming Process Detection")
        processes_layout = QtWidgets.QVBoxLayout()
        
        # Process list
        list_label = QtWidgets.QLabel("Applications that trigger Gaming Mode:")
        processes_layout.addWidget(list_label)
        
        self.process_list = QtWidgets.QListWidget()
        self.process_list.setMinimumHeight(200)
        processes_layout.addWidget(self.process_list)
        
        # Add/Remove buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.add_button = QtWidgets.QPushButton("Add Process")
        self.add_button.clicked.connect(self.add_process)
        button_layout.addWidget(self.add_button)
        
        self.remove_button = QtWidgets.QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_process)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        processes_layout.addLayout(button_layout)
        
        processes_group.setLayout(processes_layout)
        layout.addWidget(processes_group)
        
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        """Load settings from config"""
        profiles_config = self.config_manager.get_section("profiles")
        
        self.gaming_enabled_check.setChecked(profiles_config.get("gaming_mode_enabled", True))
        
        # Load gaming processes
        gaming_processes = profiles_config.get("gaming_processes", [])
        for process in gaming_processes:
            self.process_list.addItem(process)

    def save_settings(self):
        """Save settings to config"""
        self.config_manager.set_setting("profiles.gaming_mode_enabled", self.gaming_enabled_check.isChecked())
        
        # Save gaming processes
        processes = []
        for i in range(self.process_list.count()):
            processes.append(self.process_list.item(i).text())
        
        self.config_manager.set_setting("profiles.gaming_processes", processes)

    def add_process(self):
        """Add a new gaming process"""
        process_name, ok = QtWidgets.QInputDialog.getText(
            self, 
            "Add Gaming Process", 
            "Enter process name (e.g., game.exe):\n\nYou can use wildcards like *.exe"
        )
        
        if ok and process_name:
            self.process_list.addItem(process_name.strip())

    def remove_process(self):
        """Remove selected gaming process"""
        current_item = self.process_list.currentItem()
        if current_item:
            row = self.process_list.row(current_item)
            self.process_list.takeItem(row)


class StartupSettingsTab(QtWidgets.QWidget):
    """Startup and system integration settings"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        
        # Startup Group
        startup_group = QtWidgets.QGroupBox("Startup Settings")
        startup_layout = QtWidgets.QFormLayout()
        
        self.start_with_windows_check = QtWidgets.QCheckBox("Start with Windows")
        startup_layout.addRow("", self.start_with_windows_check)
        
        self.start_minimized_check = QtWidgets.QCheckBox("Start Minimized to Tray")
        startup_layout.addRow("", self.start_minimized_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Advanced Group
        advanced_group = QtWidgets.QGroupBox("Advanced Settings")
        advanced_layout = QtWidgets.QFormLayout()
        
        self.require_admin_check = QtWidgets.QCheckBox("Require Administrator Privileges")
        admin_help = QtWidgets.QLabel("Some GPU monitoring features may require admin rights")
        admin_help.setStyleSheet("color: #888888; font-style: italic; font-size: 10px;")
        admin_layout = QtWidgets.QVBoxLayout()
        admin_layout.addWidget(self.require_admin_check)
        admin_layout.addWidget(admin_help)
        advanced_layout.addRow("Permissions:", admin_layout)
        
        # GPU preference
        self.gpu_preference_combo = QtWidgets.QComboBox()
        self.gpu_preference_combo.addItems(["Auto-detect", "NVIDIA Only", "AMD Only", "Intel Only"])
        advanced_layout.addRow("GPU Preference:", self.gpu_preference_combo)
        
        # Logging
        self.logging_check = QtWidgets.QCheckBox("Enable Debug Logging")
        advanced_layout.addRow("", self.logging_check)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        self.setLayout(layout)

    def load_settings(self):
        """Load settings from config"""
        startup_config = self.config_manager.get_section("startup")
        advanced_config = self.config_manager.get_section("advanced")
        
        self.start_with_windows_check.setChecked(startup_config.get("start_with_windows", False))
        self.start_minimized_check.setChecked(startup_config.get("start_minimized", True))
        self.require_admin_check.setChecked(advanced_config.get("require_admin", False))
        self.logging_check.setChecked(advanced_config.get("logging_enabled", False))
        
        gpu_pref = advanced_config.get("gpu_vendor_preference", "auto")
        pref_mapping = {"auto": 0, "nvidia": 1, "amd": 2, "intel": 3}
        self.gpu_preference_combo.setCurrentIndex(pref_mapping.get(gpu_pref, 0))

    def save_settings(self):
        """Save settings to config"""
        self.config_manager.set_setting("startup.start_with_windows", self.start_with_windows_check.isChecked())
        self.config_manager.set_setting("startup.start_minimized", self.start_minimized_check.isChecked())
        self.config_manager.set_setting("advanced.require_admin", self.require_admin_check.isChecked())
        self.config_manager.set_setting("advanced.logging_enabled", self.logging_check.isChecked())
        
        pref_mapping = {0: "auto", 1: "nvidia", 2: "amd", 3: "intel"}
        gpu_pref = pref_mapping.get(self.gpu_preference_combo.currentIndex(), "auto")
        self.config_manager.set_setting("advanced.gpu_vendor_preference", gpu_pref)


class SettingsWindow(QtWidgets.QWidget):
    """Main settings window with tabbed interface"""
    
    def __init__(self, config_manager, profile_manager):
        super().__init__()
        self.config_manager = config_manager
        self.profile_manager = profile_manager
        
        # Prevent any window flashing during construction
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window | 
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.Tool  # Prevent taskbar appearance
        )
        self.hide()
        
        self.setWindowTitle("DevicePilot Settings")
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon))
        self.setFixedSize(700, 600)
        
        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            
            QPushButton {
                background-color: #007acc;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #005a9e;
            }
            
            QPushButton:pressed {
                background-color: #004578;
            }
            
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 2px solid #007acc;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #404040;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #007acc;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            
            QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 5px;
                background-color: #404040;
            }
            
            QListWidget {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #404040;
                alternate-background-color: #353535;
            }
        """)
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the settings interface"""
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        
        # Title
        title = QtWidgets.QLabel("DevicePilot Settings")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = ModernTabWidget()
        
        # Add tabs
        self.overlay_tab = OverlaySettingsTab(self.config_manager)
        self.metrics_tab = MetricsSettingsTab(self.config_manager)
        self.gaming_tab = GamingSettingsTab(self.config_manager, self.profile_manager)
        self.startup_tab = StartupSettingsTab(self.config_manager)
        
        self.tab_widget.addTab(self.overlay_tab, "Overlay")
        self.tab_widget.addTab(self.metrics_tab, "Metrics")
        self.tab_widget.addTab(self.gaming_tab, "Gaming")
        self.tab_widget.addTab(self.startup_tab, "Startup")
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.reset_button = QtWidgets.QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self.reset_settings)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.apply_button = QtWidgets.QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.ok_clicked)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def apply_settings(self):
        """Apply all settings"""
        self.overlay_tab.save_settings()
        self.metrics_tab.save_settings()
        self.gaming_tab.save_settings()
        self.startup_tab.save_settings()

    def ok_clicked(self):
        """Apply settings and close"""
        self.apply_settings()
        self.close()

    def reset_settings(self):
        """Reset all settings to defaults"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.config_manager.reset_to_defaults()
            # Reload settings in all tabs
            self.overlay_tab.load_settings()
            self.metrics_tab.load_settings()
            self.gaming_tab.load_settings()
            self.startup_tab.load_settings()
