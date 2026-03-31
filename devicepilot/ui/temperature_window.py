"""
Professional Temperature Monitoring Window
Comprehensive system temperature monitoring and analysis interface
"""

from PyQt6 import QtWidgets, QtCore, QtGui
import sys
from datetime import datetime, timedelta
from collections import deque
import threading
import time

class TemperatureSensorWidget(QtWidgets.QWidget):
    """Widget displaying individual temperature sensor with visual indicators"""
    
    def __init__(self, sensor_name, sensor_data):
        super().__init__()
        self.sensor_name = sensor_name
        self.sensor_data = sensor_data
        self.temperature_history = deque(maxlen=60)  # Last 60 readings
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(10)
        
        # Temperature gauge
        self.temp_gauge = TemperatureGauge()
        layout.addWidget(self.temp_gauge)
        
        # Sensor info
        info_layout = QtWidgets.QVBoxLayout()
        
        # Sensor name and label
        self.name_label = QtWidgets.QLabel(self.sensor_name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        info_layout.addWidget(self.name_label)
        
        # Current temperature
        self.temp_label = QtWidgets.QLabel("--°C")
        self.temp_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #007acc;")
        info_layout.addWidget(self.temp_label)
        
        # Status and thresholds
        self.status_label = QtWidgets.QLabel("Normal")
        self.status_label.setStyleSheet("font-size: 12px; color: #00ff00;")
        info_layout.addWidget(self.status_label)
        
        # Min/Max temperatures
        self.minmax_label = QtWidgets.QLabel("Min: --°C | Max: --°C")
        self.minmax_label.setStyleSheet("font-size: 10px; color: #888888;")
        info_layout.addWidget(self.minmax_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Mini trend chart
        self.trend_widget = MiniTrendChart()
        layout.addWidget(self.trend_widget)
        
        self.setLayout(layout)

    def update_sensor(self, sensor_data):
        """Update sensor display with new data"""
        if not sensor_data:
            return
            
        current_temp = sensor_data.get("current", 0)
        high_temp = sensor_data.get("high")
        critical_temp = sensor_data.get("critical")
        
        # Update history
        self.temperature_history.append(current_temp)
        
        # Update gauge
        self.temp_gauge.set_temperature(current_temp, high_temp, critical_temp)
        
        # Update labels
        self.temp_label.setText(f"{current_temp:.1f}°C")
        
        # Update status and color
        if critical_temp and current_temp >= critical_temp:
            status = "CRITICAL"
            color = "#ff0000"
        elif high_temp and current_temp >= high_temp:
            status = "HIGH"
            color = "#ff8000"
        elif current_temp > 70:
            status = "Warm"
            color = "#ffff00"
        elif current_temp > 50:
            status = "Normal"
            color = "#00ff00"
        else:
            status = "Cool"
            color = "#00ffff"
        
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {color};")
        self.temp_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        
        # Update min/max
        if len(self.temperature_history) > 1:
            min_temp = min(self.temperature_history)
            max_temp = max(self.temperature_history)
            self.minmax_label.setText(f"Min: {min_temp:.1f}°C | Max: {max_temp:.1f}°C")
        
        # Update trend chart
        self.trend_widget.update_data(list(self.temperature_history))


class TemperatureGauge(QtWidgets.QWidget):
    """Circular temperature gauge widget"""
    
    def __init__(self):
        super().__init__()
        self.temperature = 0
        self.high_threshold = 80
        self.critical_threshold = 90
        self.setFixedSize(80, 80)

    def set_temperature(self, temp, high=None, critical=None):
        """Set temperature and thresholds"""
        self.temperature = temp
        if high:
            self.high_threshold = high
        if critical:
            self.critical_threshold = critical
        self.update()

    def paintEvent(self, event):
        """Custom paint for temperature gauge"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(5, 5, -5, -5)
        
        # Background circle
        painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60), 2))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)
        
        # Temperature arc
        if self.temperature > 0:
            # Determine color based on temperature
            if self.temperature >= self.critical_threshold:
                color = QtGui.QColor(255, 0, 0)  # Red
            elif self.temperature >= self.high_threshold:
                color = QtGui.QColor(255, 128, 0)  # Orange
            elif self.temperature >= 50:
                color = QtGui.QColor(255, 255, 0)  # Yellow
            else:
                color = QtGui.QColor(0, 255, 0)  # Green
            
            painter.setPen(QtGui.QPen(color, 4, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap))
            
            # Calculate angle (0-270 degrees for 0-100°C range)
            max_temp = max(100, self.critical_threshold + 10)
            angle = int((self.temperature / max_temp) * 270 * 16)  # Convert to sixteenths
            
            painter.drawArc(rect, -45 * 16, angle)  # Start from -45 degrees


class MiniTrendChart(QtWidgets.QWidget):
    """Mini temperature trend chart"""
    
    def __init__(self):
        super().__init__()
        self.data = []
        self.setFixedSize(100, 50)
        self.setStyleSheet("border: 1px solid #404040; border-radius: 4px;")

    def update_data(self, data):
        """Update chart data"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        """Paint mini trend chart"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        if not self.data or len(self.data) < 2:
            return
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Calculate scaling
        min_temp = min(self.data)
        max_temp = max(self.data)
        temp_range = max_temp - min_temp if max_temp != min_temp else 1
        
        # Draw trend line
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 122, 255), 2))
        
        points = []
        for i, temp in enumerate(self.data):
            x = rect.left() + (i / (len(self.data) - 1)) * rect.width()
            y = rect.bottom() - ((temp - min_temp) / temp_range) * rect.height()
            points.append(QtCore.QPoint(int(x), int(y)))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])


class TemperatureWindow(QtWidgets.QMainWindow):
    """Main temperature monitoring window"""
    
    def __init__(self, metrics_collector=None):
        super().__init__()
        self.metrics_collector = metrics_collector
        
        # Prevent window flashing during construction
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window | 
            QtCore.Qt.WindowType.WindowCloseButtonHint
        )
        self.hide()
        
        self.setWindowTitle("Temperature Monitor")
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.resize(800, 600)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
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
        """)
        
        self.sensor_widgets = {}
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.refresh_temperatures)
        
        self.setup_ui()
        self.setup_toolbar()

    def setup_ui(self):
        """Setup the main interface"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("System Temperature Monitor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #007acc;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Auto-refresh toggle
        self.auto_refresh_cb = QtWidgets.QCheckBox("Auto Refresh")
        self.auto_refresh_cb.setChecked(True)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        header_layout.addWidget(self.auto_refresh_cb)
        
        layout.addLayout(header_layout)
        
        # Temperature summary cards
        self.summary_widget = self.create_summary_widget()
        layout.addWidget(self.summary_widget)
        
        # Sensors scroll area
        self.sensors_scroll = QtWidgets.QScrollArea()
        self.sensors_widget = QtWidgets.QWidget()
        self.sensors_layout = QtWidgets.QVBoxLayout()
        self.sensors_widget.setLayout(self.sensors_layout)
        self.sensors_scroll.setWidget(self.sensors_widget)
        self.sensors_scroll.setWidgetResizable(True)
        self.sensors_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #353535;
            }
        """)
        
        layout.addWidget(self.sensors_scroll)
        central_widget.setLayout(layout)
        
        # Start auto-refresh
        self.toggle_auto_refresh(True)

    def create_summary_widget(self):
        """Create temperature summary widget"""
        group = QtWidgets.QGroupBox("Temperature Summary")
        layout = QtWidgets.QGridLayout()
        
        # Summary cards
        self.cpu_summary = self.create_summary_card("CPU", "#ff6b35")
        self.gpu_summary = self.create_summary_card("GPU", "#45b7d1")
        self.system_summary = self.create_summary_card("System", "#f9ca24")
        self.highest_summary = self.create_summary_card("Highest", "#e74c3c")
        
        layout.addWidget(self.cpu_summary, 0, 0)
        layout.addWidget(self.gpu_summary, 0, 1)
        layout.addWidget(self.system_summary, 0, 2)
        layout.addWidget(self.highest_summary, 0, 3)
        
        group.setLayout(layout)
        return group

    def create_summary_card(self, title, color):
        """Create a summary temperature card"""
        widget = QtWidgets.QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: #353535;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QtWidgets.QVBoxLayout()
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        temp_label = QtWidgets.QLabel("--°C")
        temp_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        temp_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(temp_label)
        
        widget.setLayout(layout)
        widget.temp_label = temp_label  # Store reference for updates
        return widget

    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = self.addToolBar("Main")
        toolbar.setStyleSheet("""
            QToolBar {
                border: none;
                background-color: #353535;
                spacing: 5px;
                padding: 5px;
            }
        """)
        
        # Refresh action
        refresh_action = QtGui.QAction("Refresh Now", self)
        refresh_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        refresh_action.triggered.connect(self.refresh_temperatures)
        toolbar.addAction(refresh_action)
        
        # Export action
        export_action = QtGui.QAction("Export Data", self)
        export_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))
        export_action.triggered.connect(self.export_temperature_data)
        toolbar.addAction(export_action)

    def show_window(self):
        """Properly show the window"""
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, False)
        self.refresh_temperatures()  # Load initial data
        self.show()
        self.raise_()
        self.activateWindow()

    def refresh_temperatures(self):
        """Refresh temperature data"""
        if not self.metrics_collector:
            return
            
        try:
            temp_data = self.metrics_collector.get_temperature_metrics()
            self.update_display(temp_data)
        except Exception as e:
            print(f"Error refreshing temperatures: {e}")

    def update_display(self, temp_data):
        """Update temperature display"""
        if not temp_data:
            return
            
        # Update summary cards
        summary = temp_data.get("summary", {})
        self.cpu_summary.temp_label.setText(f"{summary.get('cpu_temp', 0):.1f}°C")
        self.gpu_summary.temp_label.setText(f"{summary.get('gpu_temp', 0):.1f}°C")
        self.system_summary.temp_label.setText(f"{summary.get('motherboard_temp', 0):.1f}°C")
        self.highest_summary.temp_label.setText(f"{summary.get('highest_temp', 0):.1f}°C")
        
        # Update sensor widgets
        sensors = temp_data.get("sensors", {})
        
        # Remove widgets for sensors that no longer exist
        existing_sensors = set(self.sensor_widgets.keys())
        current_sensors = set()
        
        for sensor_name, sensor_list in sensors.items():
            for i, sensor_data in enumerate(sensor_list):
                sensor_key = f"{sensor_name}_{i}"
                current_sensors.add(sensor_key)
                
                if sensor_key not in self.sensor_widgets:
                    # Create new sensor widget
                    widget = TemperatureSensorWidget(
                        f"{sensor_name} - {sensor_data.get('label', 'Unknown')}", 
                        sensor_data
                    )
                    self.sensor_widgets[sensor_key] = widget
                    self.sensors_layout.addWidget(widget)
                
                # Update existing widget
                self.sensor_widgets[sensor_key].update_sensor(sensor_data)
        
        # Remove widgets for sensors that no longer exist
        for sensor_key in existing_sensors - current_sensors:
            widget = self.sensor_widgets.pop(sensor_key)
            self.sensors_layout.removeWidget(widget)
            widget.deleteLater()

    def toggle_auto_refresh(self, enabled):
        """Toggle auto-refresh"""
        if enabled:
            self.update_timer.start(2000)  # Update every 2 seconds
        else:
            self.update_timer.stop()

    def export_temperature_data(self):
        """Export temperature data"""
        if not self.metrics_collector:
            return
            
        try:
            temp_data = self.metrics_collector.get_temperature_metrics()
            
            # Create export data
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "temperature_data": temp_data,
                "sensor_history": {
                    key: list(widget.temperature_history) 
                    for key, widget in self.sensor_widgets.items()
                }
            }
            
            # Save to file
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Export Temperature Data",
                f"temperature_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                import json
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                
                QtWidgets.QMessageBox.information(
                    self, "Export Complete", 
                    f"Temperature data exported to {file_path}"
                )
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Export Error", 
                f"Failed to export temperature data: {str(e)}"
            )

    def closeEvent(self, event):
        """Handle window close"""
        self.update_timer.stop()
        event.accept()
