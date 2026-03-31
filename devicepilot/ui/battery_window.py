"""
Professional Battery Health Analysis Window
Comprehensive battery monitoring and health reporting interface
"""

from PyQt6 import QtWidgets, QtCore, QtGui
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    QWebEngineView = None

import sys
import os
from pathlib import Path
from devicepilot.core.battery import BatteryManager
import json
from datetime import datetime


class BatteryHealthWidget(QtWidgets.QWidget):
    """Widget displaying battery health information with visual indicators"""
    
    def __init__(self, health_score=0, status="Unknown"):
        super().__init__()
        self.health_score = health_score
        self.status = status
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)
        
        # Health score display
        score_layout = QtWidgets.QHBoxLayout()
        
        # Circular progress indicator
        self.progress_widget = CircularProgressWidget(self.health_score)
        score_layout.addWidget(self.progress_widget)
        
        # Health info
        info_layout = QtWidgets.QVBoxLayout()
        
        self.health_label = QtWidgets.QLabel(f"{self.health_score:.1f}%")
        self.health_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #007acc;")
        info_layout.addWidget(self.health_label)
        
        self.status_label = QtWidgets.QLabel(self.status)
        self.status_label.setStyleSheet("font-size: 16px; color: #888888;")
        info_layout.addWidget(self.status_label)
        
        score_layout.addLayout(info_layout)
        score_layout.addStretch()
        
        layout.addLayout(score_layout)
        self.setLayout(layout)

    def update_health(self, health_score, status):
        """Update health display"""
        self.health_score = health_score
        self.status = status
        
        self.progress_widget.set_value(health_score)
        self.health_label.setText(f"{health_score:.1f}%")
        self.status_label.setText(status)
        
        # Update color based on health
        if health_score >= 80:
            color = "#27ae60"  # Green
        elif health_score >= 60:
            color = "#f39c12"  # Orange
        else:
            color = "#e74c3c"  # Red
        
        self.health_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")


class CircularProgressWidget(QtWidgets.QWidget):
    """Custom circular progress widget for health display"""
    
    def __init__(self, value=0):
        super().__init__()
        self.value = value
        self.setFixedSize(120, 120)

    def set_value(self, value):
        """Set progress value and update display"""
        self.value = value
        self.update()

    def paintEvent(self, event):
        """Custom paint for circular progress"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Calculate perfect circle dimensions
        size = min(self.width(), self.height())
        margin = 10
        circle_size = size - (2 * margin)
        pen_width = 8
        
        # Center the circle perfectly
        x = (self.width() - circle_size) // 2
        y = (self.height() - circle_size) // 2
        rect = QtCore.QRect(x, y, circle_size, circle_size)
        
        # Background circle (complete ring)
        painter.setPen(QtGui.QPen(QtGui.QColor(40, 40, 40, 100), pen_width, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawEllipse(rect)
        
        # Progress arc (only if there's a value)
        if self.value > 0:
            # Color based on value
            if self.value >= 80:
                color = QtGui.QColor(39, 174, 96)  # Green
            elif self.value >= 60:
                color = QtGui.QColor(243, 156, 18)  # Orange
            else:
                color = QtGui.QColor(231, 76, 60)  # Red
            
            # Draw progress arc with round caps for smooth appearance
            painter.setPen(QtGui.QPen(color, pen_width, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap))
            
            # Calculate angle (0-360 degrees, starting from top)
            # -90 degrees to start from top, clockwise
            start_angle = -90 * 16  # Convert to sixteenths of degrees
            span_angle = int((self.value / 100) * 360 * 16)  # Convert to sixteenths of degrees
            
            painter.drawArc(rect, start_angle, span_angle)


class BatteryDetailsWidget(QtWidgets.QWidget):
    """Widget showing detailed battery specifications"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout()
        layout.setSpacing(15)
        
        # Create labels for battery details
        self.name_label = QtWidgets.QLabel("N/A")
        self.manufacturer_label = QtWidgets.QLabel("N/A")
        self.chemistry_label = QtWidgets.QLabel("N/A")
        self.design_capacity_label = QtWidgets.QLabel("N/A")
        self.full_capacity_label = QtWidgets.QLabel("N/A")
        self.cycle_count_label = QtWidgets.QLabel("N/A")
        self.serial_label = QtWidgets.QLabel("N/A")
        
        # Style labels
        for label in [self.name_label, self.manufacturer_label, self.chemistry_label,
                     self.design_capacity_label, self.full_capacity_label, 
                     self.cycle_count_label, self.serial_label]:
            label.setStyleSheet("color: #ffffff; font-weight: bold;")
        
        layout.addRow("Name:", self.name_label)
        layout.addRow("Manufacturer:", self.manufacturer_label)
        layout.addRow("Chemistry:", self.chemistry_label)
        layout.addRow("Design Capacity:", self.design_capacity_label)
        layout.addRow("Full Charge Capacity:", self.full_capacity_label)
        layout.addRow("Cycle Count:", self.cycle_count_label)
        layout.addRow("Serial Number:", self.serial_label)
        
        self.setLayout(layout)

    def update_details(self, battery_info):
        """Update battery details display"""
        if not battery_info:
            return
        
        self.name_label.setText(battery_info.get('name', 'N/A'))
        self.manufacturer_label.setText(battery_info.get('manufacturer', 'N/A'))
        self.chemistry_label.setText(battery_info.get('chemistry', 'N/A'))
        
        # Format capacities
        design_cap = battery_info.get('design_capacity_mwh')
        if design_cap:
            self.design_capacity_label.setText(f"{design_cap:,} mWh")
        
        full_cap = battery_info.get('full_charge_capacity_mwh')
        if full_cap:
            self.full_capacity_label.setText(f"{full_cap:,} mWh")
        
        cycle_count = battery_info.get('cycle_count')
        if cycle_count:
            self.cycle_count_label.setText(f"{cycle_count:,} cycles")
        
        self.serial_label.setText(battery_info.get('serial_number', 'N/A'))


class RecommendationsWidget(QtWidgets.QWidget):
    """Widget displaying battery care recommendations"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        title = QtWidgets.QLabel("Battery Care Recommendations")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #007acc; margin-bottom: 10px;")
        layout.addWidget(title)
        
        self.recommendations_list = QtWidgets.QListWidget()
        self.recommendations_list.setStyleSheet("""
            QListWidget {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #404040;
                color: #ffffff;
            }
            QListWidget::item:last {
                border-bottom: none;
            }
        """)
        layout.addWidget(self.recommendations_list)
        
        self.setLayout(layout)

    def update_recommendations(self, recommendations):
        """Update recommendations list"""
        self.recommendations_list.clear()
        for rec in recommendations:
            item = QtWidgets.QListWidgetItem(rec)
            self.recommendations_list.addItem(item)


class BatteryWindow(QtWidgets.QMainWindow):
    """Main battery health monitoring window"""
    
    def __init__(self):
        super().__init__()
        self.battery_manager = BatteryManager()
        self.report_data = {}
        
        # Prevent any window flashing during construction
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, True)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window | 
            QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.Tool  # Prevent taskbar appearance
        )
        self.hide()
        
        self.setWindowTitle("Battery Health Monitor")
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView))
        self.resize(900, 700)
        
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
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
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
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        self.setup_ui()
        self.setup_toolbar()
        self.setup_statusbar()

    def setup_toolbar(self):
        """Setup toolbar with actions"""
        toolbar = self.addToolBar("Main")
        toolbar.setStyleSheet("""
            QToolBar {
                border: none;
                background-color: #353535;
                spacing: 5px;
                padding: 5px;
            }
        """)
        
        # Generate report action
        generate_action = QtGui.QAction("Generate Report", self)
        generate_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogNewFolder))
        generate_action.triggered.connect(self.generate_report)
        toolbar.addAction(generate_action)
        
        # Refresh action
        refresh_action = QtGui.QAction("Refresh", self)
        refresh_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_BrowserReload))
        refresh_action.triggered.connect(self.refresh_data)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # Export action
        export_action = QtGui.QAction("Export Data", self)
        export_action.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_DialogSaveButton))
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)

    def setup_statusbar(self):
        """Setup status bar"""
        self.statusBar().showMessage("Ready - Click 'Generate Report' to analyze battery health")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #353535;
                color: #ffffff;
                border: none;
                padding: 5px;
            }
        """)

    def setup_ui(self):
        """Setup the main interface"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with title and generate button
        header_layout = QtWidgets.QHBoxLayout()
        
        title = QtWidgets.QLabel("Battery Health Monitor")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #007acc;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.generate_button = QtWidgets.QPushButton("Generate New Report")
        self.generate_button.clicked.connect(self.generate_report)
        self.generate_button.setMinimumWidth(180)
        header_layout.addWidget(self.generate_button)
        
        layout.addLayout(header_layout)
        
        # Main content area with tabs
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview")
        
        # Details tab
        self.details_tab = self.create_details_tab()
        self.tab_widget.addTab(self.details_tab, "Details")
        
        # Report tab
        self.report_tab = self.create_report_tab()
        self.tab_widget.addTab(self.report_tab, "Full Report")
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)

    def create_overview_tab(self):
        """Create overview tab with health summary"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(30)
        
        # Left side - Health indicator
        health_group = QtWidgets.QGroupBox("Battery Health")
        health_layout = QtWidgets.QVBoxLayout()
        
        self.health_widget = BatteryHealthWidget()
        health_layout.addWidget(self.health_widget)
        
        health_group.setLayout(health_layout)
        layout.addWidget(health_group)
        
        # Right side - Details and recommendations
        right_layout = QtWidgets.QVBoxLayout()
        
        # Battery details
        details_group = QtWidgets.QGroupBox("Battery Information")
        self.details_widget = BatteryDetailsWidget()
        details_group.setLayout(QtWidgets.QVBoxLayout())
        details_group.layout().addWidget(self.details_widget)
        right_layout.addWidget(details_group)
        
        # Recommendations
        rec_group = QtWidgets.QGroupBox("Recommendations")
        self.recommendations_widget = RecommendationsWidget()
        rec_group.setLayout(QtWidgets.QVBoxLayout())
        rec_group.layout().addWidget(self.recommendations_widget)
        right_layout.addWidget(rec_group)
        
        layout.addLayout(right_layout)
        widget.setLayout(layout)
        return widget

    def create_details_tab(self):
        """Create detailed information tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Statistics and analysis
        self.details_text = QtWidgets.QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                background-color: #353535;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        
        layout.addWidget(self.details_text)
        widget.setLayout(layout)
        return widget

    def create_report_tab(self):
        """Create full HTML report tab"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # Web view for HTML report
        if WEB_ENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setStyleSheet("""
                QWebEngineView {
                    border: 1px solid #404040;
                    border-radius: 8px;
                }
            """)
            layout.addWidget(self.web_view)
        else:
            # Fallback if QtWebEngine is not available
            self.web_view = None
            fallback_label = QtWidgets.QLabel("Web view not available. Install PyQt5-WebEngine for HTML report viewing.")
            fallback_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            fallback_label.setStyleSheet("color: #888888; font-style: italic; padding: 20px;")
            layout.addWidget(fallback_label)
        
        # Open in browser button
        browser_button = QtWidgets.QPushButton("Open Report in Browser")
        browser_button.clicked.connect(self.open_in_browser)
        layout.addWidget(browser_button)
        
        widget.setLayout(layout)
        return widget

    def generate_report(self):
        """Generate a new battery report"""
        self.statusBar().showMessage("Generating battery report...")
        self.generate_button.setEnabled(False)
        
        try:
            # Generate report
            report_path = self.battery_manager.generate_battery_report()
            
            if report_path:
                # Parse report
                self.report_data = self.battery_manager.parse_battery_report(report_path)
                self.current_report_path = report_path
                
                # Update UI
                self.update_overview()
                self.update_details()
                self.update_report_view()
                
                self.statusBar().showMessage(f"Report generated successfully: {report_path.name}")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to generate battery report.")
                self.statusBar().showMessage("Failed to generate report")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error generating report: {str(e)}")
            self.statusBar().showMessage("Error generating report")
        
        finally:
            self.generate_button.setEnabled(True)

    def update_overview(self):
        """Update overview tab with report data"""
        if not self.report_data:
            return
        
        # Update health display
        health_analysis = self.report_data.get('health_analysis', {})
        health_score = health_analysis.get('health_score', 0)
        overall_health = health_analysis.get('overall_health', 'Unknown')
        
        self.health_widget.update_health(health_score, overall_health)
        
        # Update details
        battery_info = self.report_data.get('battery_info', [])
        if battery_info:
            self.details_widget.update_details(battery_info[0])
        
        # Update recommendations
        recommendations = health_analysis.get('recommendations', [])
        warnings = health_analysis.get('warnings', [])
        all_recommendations = warnings + recommendations
        
        if not all_recommendations:
            # Add general recommendations
            all_recommendations = self.battery_manager.get_battery_recommendations(
                health_score, 
                battery_info[0].get('cycle_count') if battery_info else None
            )
        
        self.recommendations_widget.update_recommendations(all_recommendations)

    def update_details(self):
        """Update details tab with comprehensive information"""
        if not self.report_data:
            return
        
        details_text = ""
        
        # System information
        system_info = self.report_data.get('system_info', {})
        if system_info:
            details_text += "=== SYSTEM INFORMATION ===\n"
            details_text += f"Computer: {system_info.get('computer_name', 'N/A')}\n"
            details_text += f"Platform: {system_info.get('platform_role', 'N/A')}\n"
            details_text += f"Report Time: {system_info.get('report_time', 'N/A')}\n\n"
        
        # Battery information
        battery_info = self.report_data.get('battery_info', [])
        for i, battery in enumerate(battery_info):
            details_text += f"=== BATTERY {i+1} ===\n"
            details_text += f"Name: {battery.get('name', 'N/A')}\n"
            details_text += f"Manufacturer: {battery.get('manufacturer', 'N/A')}\n"
            details_text += f"Chemistry: {battery.get('chemistry', 'N/A')}\n"
            details_text += f"Serial Number: {battery.get('serial_number', 'N/A')}\n"
            
            design_cap = battery.get('design_capacity_mwh')
            full_cap = battery.get('full_charge_capacity_mwh')
            if design_cap and full_cap:
                health_pct = (full_cap / design_cap) * 100
                details_text += f"Design Capacity: {design_cap:,} mWh\n"
                details_text += f"Full Charge Capacity: {full_cap:,} mWh\n"
                details_text += f"Health: {health_pct:.1f}%\n"
            
            cycle_count = battery.get('cycle_count')
            if cycle_count:
                details_text += f"Cycle Count: {cycle_count:,}\n"
            
            details_text += "\n"
        
        # Health analysis
        health_analysis = self.report_data.get('health_analysis', {})
        if health_analysis:
            details_text += "=== HEALTH ANALYSIS ===\n"
            details_text += f"Overall Health: {health_analysis.get('overall_health', 'Unknown')}\n"
            details_text += f"Health Score: {health_analysis.get('health_score', 0):.1f}%\n"
            
            statistics = health_analysis.get('statistics', {})
            if statistics:
                details_text += "\nStatistics:\n"
                for key, value in statistics.items():
                    details_text += f"  {key.replace('_', ' ').title()}: {value}\n"
            
            warnings = health_analysis.get('warnings', [])
            if warnings:
                details_text += "\nWarnings:\n"
                for warning in warnings:
                    details_text += f"  ⚠️ {warning}\n"
            
            recommendations = health_analysis.get('recommendations', [])
            if recommendations:
                details_text += "\nRecommendations:\n"
                for rec in recommendations:
                    details_text += f"  💡 {rec}\n"
        
        self.details_text.setPlainText(details_text)

    def update_report_view(self):
        """Update the web view with HTML report"""
        if hasattr(self, 'current_report_path') and self.web_view:
            try:
                file_url = QtCore.QUrl.fromLocalFile(str(self.current_report_path.absolute()))
                self.web_view.load(file_url)
            except Exception as e:
                print(f"Error loading web view: {e}")

    def refresh_data(self):
        """Refresh battery data"""
        self.generate_report()

    def export_data(self):
        """Export battery data to JSON"""
        if not self.report_data:
            QtWidgets.QMessageBox.information(self, "No Data", "Generate a report first.")
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            "Export Battery Data",
            f"battery_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            if self.battery_manager.export_battery_data(self.report_data, Path(file_path)):
                QtWidgets.QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Failed to export data")

    def show_window(self):
        """Properly show the window without flashing"""
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, False)
        self.show()
        self.raise_()
        self.activateWindow()

    def open_in_browser(self):
        """Open current report in system browser"""
        if hasattr(self, 'current_report_path'):
            import webbrowser
            webbrowser.open(str(self.current_report_path.absolute()))
        else:
            QtWidgets.QMessageBox.information(self, "No Report", "Generate a report first.")
