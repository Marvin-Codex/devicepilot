"""
Professional Overlay Window with Modern Design
Advanced transparent overlay with docking, themes, and smooth animations
"""

import sys
import math
from PyQt6 import QtWidgets, QtCore, QtGui
import ctypes
from ctypes import wintypes

# Windows constants for advanced window effects
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
WS_EX_TOOLWINDOW = 0x00000080


def make_click_through(hwnd):
    """Enable click-through for the window"""
    old = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, old | WS_EX_LAYERED | WS_EX_TRANSPARENT)


def remove_click_through(hwnd):
    """Disable click-through for the window"""
    old = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    new = old & ~WS_EX_TRANSPARENT
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new)


class MetricWidget(QtWidgets.QWidget):
    """Individual metric display widget with icon and value"""
    
    def __init__(self, name, icon_text, unit="", color="#007acc"):
        super().__init__()
        self.name = name
        self.unit = unit
        self.color = color
        self.current_display_color = color  # For color animations
        self.value = 0
        
        # Initialize all animated properties first
        self._value_animated = 0
        self._color_factor = 1.0  # Factor for color transitions
        self._pulse_factor = 1.0  # Factor for pulse effect
        self._breathing_factor = 1.0  # Factor for breathing effect
        self._target_color = color
        
        self.setFixedSize(80, 75)  # Increased height to accommodate external label
        
        # Enhanced animation for value changes
        self.animation = QtCore.QPropertyAnimation(self, b"value_animated")
        self.animation.setDuration(1500)  # Longer animation to be more visible
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.OutBack)  # More elastic feel
        
        # Animation for color transitions
        self.color_animation = QtCore.QPropertyAnimation(self, b"color_factor")
        self.color_animation.setDuration(400)
        self.color_animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)
        
        # Pulse animation for significant changes
        self.pulse_animation = QtCore.QPropertyAnimation(self, b"pulse_factor")
        self.pulse_animation.setDuration(600)
        self.pulse_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutBack)
        
        # Subtle breathing animation for idle state
        self.breathing_animation = QtCore.QPropertyAnimation(self, b"breathing_factor")
        self.breathing_animation.setDuration(3000)
        self.breathing_animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutSine)
        self.breathing_animation.setStartValue(0.95)
        self.breathing_animation.setEndValue(1.05)
        self.breathing_animation.setLoopCount(-1)  # Infinite loop
        self.breathing_animation.setDirection(QtCore.QAbstractAnimation.Direction.Forward)
        
        # Start breathing animation
        self.breathing_animation.start()
        
    def set_value(self, value):
        """Set value with enhanced smooth animation"""
        # Check for significant changes to trigger pulse effect
        value_change = abs(value - self._value_animated)
        if value_change > 10:  # Significant change threshold
            self.trigger_pulse()
        
        # Always animate value changes for better visual feedback
        if value_change > 1.0:  # Increase threshold to reduce frequent animations
            self.animation.stop()  # Stop any existing animation
            self.animation.setDuration(1500)  # Ensure consistent duration
            self.animation.setStartValue(self._value_animated)
            self.animation.setEndValue(value)
            self.animation.start()
        else:
            # For very small changes, set directly
            self._value_animated = value
            self.update()
        
        self.value = value
    
    def trigger_pulse(self):
        """Trigger a pulse animation for significant changes"""
        self.pulse_animation.stop()
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(1.3)
        self.pulse_animation.finished.connect(self.pulse_back)
        self.pulse_animation.start()
    
    def pulse_back(self):
        """Return pulse to normal"""
        self.pulse_animation.finished.disconnect()
        self.pulse_animation.setStartValue(1.3)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.start()
    
    def get_pulse_factor(self):
        return self._pulse_factor
    
    def set_pulse_factor(self, factor):
        self._pulse_factor = factor
        self.update()
    
    pulse_factor = QtCore.pyqtProperty(float, get_pulse_factor, set_pulse_factor)
    
    def get_breathing_factor(self):
        return self._breathing_factor
    
    def set_breathing_factor(self, factor):
        self._breathing_factor = factor
        self.update()
    
    breathing_factor = QtCore.pyqtProperty(float, get_breathing_factor, set_breathing_factor)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to show detailed window"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            # Get the overlay window parent
            overlay = self.parent()
            while overlay and not isinstance(overlay, OverlayWindow):
                overlay = overlay.parent()
            
            if overlay and overlay.main_app:
                # Open appropriate detailed window based on widget type
                if self.name == "TEMP" and hasattr(overlay.main_app, 'show_temperature_monitor'):
                    overlay.main_app.show_temperature_monitor()
                elif self.name == "BAT" and hasattr(overlay.main_app, 'show_battery_health'):
                    overlay.main_app.show_battery_health()
        
        super().mouseDoubleClickEvent(event)
    
    def set_color(self, new_color):
        """Set color with smooth transition"""
        if new_color != self.color:
            self._target_color = new_color
            self.color_animation.setStartValue(0.0)
            self.color_animation.setEndValue(1.0)
            self.color_animation.start()
    
    def get_color_factor(self):
        return self._color_factor
    
    def set_color_factor(self, factor):
        """Interpolate between current and target color"""
        self._color_factor = factor
        if hasattr(self, '_target_color'):
            # Interpolate colors
            current_color = QtGui.QColor(self.color)
            target_color = QtGui.QColor(self._target_color)
            
            # Linear interpolation of RGB values
            r = int(current_color.red() + (target_color.red() - current_color.red()) * factor)
            g = int(current_color.green() + (target_color.green() - current_color.green()) * factor)
            b = int(current_color.blue() + (target_color.blue() - current_color.blue()) * factor)
            
            interpolated_color = QtGui.QColor(r, g, b)
            self.current_display_color = interpolated_color.name()
            
            # When animation completes, update the main color
            if factor >= 1.0:
                self.color = self._target_color
                self.current_display_color = self.color
        
        self.update()
    
    color_factor = QtCore.pyqtProperty(float, get_color_factor, set_color_factor)
        
    def get_value_animated(self):
        return self._value_animated
    
    def set_value_animated(self, value):
        self._value_animated = value
        self.update()
    
    value_animated = QtCore.pyqtProperty(float, get_value_animated, set_value_animated)
    
    def paintEvent(self, event):
        """Custom paint method for modern design"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Background with rounded corners and pulse effect
        painter.setBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30, 180)))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        
        # Apply pulse scaling
        if hasattr(self, '_pulse_factor') and self._pulse_factor != 1.0:
            painter.save()
            center = rect.center()
            painter.translate(center)
            painter.scale(self._pulse_factor, self._pulse_factor)
            painter.translate(-center)
        
        painter.drawRoundedRect(rect, 8, 8)
        
        if hasattr(self, '_pulse_factor') and self._pulse_factor != 1.0:
            painter.restore()
        
        # Circular progress ring with enhanced visuals
        if self.value > 0:
            # Create a perfect circular area within the widget
            circle_size = min(rect.width(), rect.height()) - 12  # Leave margin
            circle_x = rect.x() + (rect.width() - circle_size) // 2
            circle_y = rect.y() + (rect.height() - circle_size) // 2
            circle_rect = QtCore.QRect(circle_x, circle_y, circle_size, circle_size)
            
            # Background circle (subtle with glow effect)
            painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60, 120), 3))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawEllipse(circle_rect)
            
            # Outer glow effect for progress arc with breathing
            glow_intensity = self._breathing_factor if hasattr(self, '_breathing_factor') else 1.0
            for i in range(3):
                glow_pen = QtGui.QPen(QtGui.QColor(self.current_display_color), 4 + i, 
                                    QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap)
                glow_pen.setColor(QtGui.QColor(self.current_display_color))
                glow_color = glow_pen.color()
                glow_color.setAlpha(int((30 - i * 8) * glow_intensity))  # Breathing glow intensity
                glow_pen.setColor(glow_color)
                painter.setPen(glow_pen)
                
                # Draw the glow arc
                start_angle = -90 * 16  # Start from top
                span_angle = int((self._value_animated / 100) * 360 * 16)
                painter.drawArc(circle_rect.adjusted(-i, -i, i, i), start_angle, span_angle)
            
            # Main progress arc with gradient effect
            center_point = QtCore.QPointF(circle_rect.center())
            gradient = QtGui.QConicalGradient(center_point, -90)
            base_color = QtGui.QColor(self.current_display_color)
            bright_color = base_color.lighter(150)
            gradient.setColorAt(0, bright_color)
            gradient.setColorAt(0.5, base_color)
            gradient.setColorAt(1, base_color.darker(120))
            
            gradient_pen = QtGui.QPen(QtGui.QBrush(gradient), 4, 
                                   QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap)
            painter.setPen(gradient_pen)
            
            # Draw the main progress arc
            start_angle = -90 * 16  # Start from top (-90 degrees)
            span_angle = int((self._value_animated / 100) * 360 * 16)  # Convert to sixteenths of degrees
            painter.drawArc(circle_rect, start_angle, span_angle)
            
            # Add a subtle inner highlight
            if self._value_animated > 5:  # Only show when there's meaningful progress
                painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 60), 1))
                painter.drawArc(circle_rect.adjusted(2, 2, -2, -2), start_angle, span_angle)
        
        # Icon/Label (first letter of metric name)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        icon_rect = QtCore.QRect(rect.x(), rect.y() + 5, rect.width(), 20)
        painter.drawText(icon_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.name[0].upper())
        
        # Value text
        font.setPointSize(12)
        painter.setFont(font)
        value_text = f"{self._value_animated:.0f}{self.unit}"
        value_rect = QtCore.QRect(rect.x(), rect.y() + 25, rect.width(), 20)
        painter.drawText(value_rect, QtCore.Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Full name label below the circular widget
        font.setPointSize(7)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QtGui.QPen(QtGui.QColor(180, 180, 180)))
        name_rect = QtCore.QRect(rect.x(), rect.y() + 50, rect.width(), 15)
        painter.drawText(name_rect, QtCore.Qt.AlignmentFlag.AlignCenter, self.name.upper())


class OverlayWindow(QtWidgets.QWidget):
    """Main overlay window with professional design and animations"""
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        
        # Window properties - Set all flags before showing
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool |
            QtCore.Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, True)  # Prevent flash
        
        # State variables
        self._drag_pos = None
        self._click_through = False
        self._is_gaming_mode = False
        self._dock_side = "none"
        
        # Store reference to main app for opening detailed windows
        self.main_app = None
        
        # Initialize UI
        self.setup_ui()
        self.load_theme()
        
        # Position and size
        self.resize(400, 135)  # Increased height for external labels
        self.move(50, 50)
        
        # Load saved dock position
        overlay_config = self.config_manager.get_section("overlay")
        saved_dock_side = overlay_config.get("dock_side", "none")
        if saved_dock_side != "none":
            self._dock_side = saved_dock_side
            self.dock_to_side(saved_dock_side)
        
        # Animations
        self.setup_animations()
        
        # Show/hide animations
        self.fade_animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        
        # Auto-hide timer for gaming mode
        self.auto_hide_timer = QtCore.QTimer()
        self.auto_hide_timer.timeout.connect(self.check_auto_hide)
        self.auto_hide_timer.start(5000)  # Check every 5 seconds
        
        # Setup keyboard shortcuts for docking
        self.setup_keyboard_shortcuts()
        
        # Enable normal showing now that setup is complete
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen, False)

    def set_main_app(self, main_app):
        """Set reference to main application"""
        self.main_app = main_app

    def setup_ui(self):
        """Setup the user interface"""
        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.setSpacing(15)
        
        # Create metric widgets
        self.cpu_widget = MetricWidget("CPU", "C", "%", "#ff6b35")
        self.ram_widget = MetricWidget("RAM", "R", "%", "#4ecdc4")
        self.gpu_widget = MetricWidget("GPU", "G", "%", "#45b7d1")
        self.temp_widget = MetricWidget("TEMP", "T", "°C", "#f9ca24")
        self.battery_widget = MetricWidget("BAT", "B", "%", "#6c5ce7")
        self.fps_widget = MetricWidget("FPS", "F", "", "#a55eea")
        
        # Add widgets to layout
        self.main_layout.addWidget(self.cpu_widget)
        self.main_layout.addWidget(self.ram_widget)
        self.main_layout.addWidget(self.gpu_widget)
        self.main_layout.addWidget(self.temp_widget)
        self.main_layout.addWidget(self.battery_widget)
        self.main_layout.addWidget(self.fps_widget)
        
        # Gaming mode - show FPS widget only when needed
        self.fps_widget.hide()
        
        # Update widget visibility based on configuration
        self.update_widget_visibility()
        
        self.setLayout(self.main_layout)
        
        # Context menu
        self.setup_context_menu()

    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show context menu"""
        menu = QtWidgets.QMenu(self)
        
        # Toggle click-through
        click_through_action = menu.addAction("Toggle Click-through")
        click_through_action.triggered.connect(self.toggle_click_through)
        
        # Dock options
        dock_menu = menu.addMenu("Dock to...")
        
        dock_actions = [
            ("None (Ctrl+0)", "none"),
            ("Center (Ctrl+5)", "center"),
            ("Top (Ctrl+8)", "top"),
            ("Top-Left (Ctrl+7)", "top-left"),
            ("Top-Right (Ctrl+9)", "top-right"),
            ("Bottom (Ctrl+2)", "bottom"),
            ("Bottom-Left (Ctrl+1)", "bottom-left"),
            ("Bottom-Right (Ctrl+3)", "bottom-right"),
            ("Left (Ctrl+4)", "left"),
            ("Right (Ctrl+6)", "right")
        ]
        
        for text, dock_side in dock_actions:
            action = dock_menu.addAction(text)
            action.triggered.connect(lambda checked, side=dock_side: self.dock_to_side(side))
            if self._dock_side == dock_side:
                action.setCheckable(True)
                action.setChecked(True)
        
        menu.addSeparator()
        
        # Hide overlay
        hide_action = menu.addAction("Hide Overlay")
        hide_action.triggered.connect(self.hide)
        
        menu.exec(self.mapToGlobal(position))

    def setup_animations(self):
        """Setup smooth animations"""
        self.resize_animation = QtCore.QPropertyAnimation(self, b"geometry")
        self.resize_animation.setDuration(300)
        self.resize_animation.setEasingCurve(QtCore.QEasingCurve.Type.OutCubic)

    def load_theme(self):
        """Load theme settings and apply styling"""
        theme = self.config_manager.get_section("theme")
        
        # Set opacity
        overlay_config = self.config_manager.get_section("overlay")
        self.setWindowOpacity(overlay_config.get("opacity", 0.9))
    
    def update_widget_visibility(self):
        """Update widget visibility based on configuration"""
        metrics_config = self.config_manager.get_section("metrics")
        
        # Show/hide widgets based on configuration
        self.cpu_widget.setVisible(metrics_config.get("show_cpu", True))
        self.ram_widget.setVisible(metrics_config.get("show_ram", True))
        self.gpu_widget.setVisible(metrics_config.get("show_gpu", True))
        self.temp_widget.setVisible(metrics_config.get("show_temperature", True))
        self.battery_widget.setVisible(metrics_config.get("show_battery", True))
        
        # FPS widget is handled separately in gaming mode
        if not self._is_gaming_mode:
            self.fps_widget.setVisible(False)
        else:
            self.fps_widget.setVisible(metrics_config.get("show_fps", True))

    @QtCore.pyqtSlot(dict, bool)
    def update_metrics(self, metrics, is_gaming):
        """Update display with new metrics"""
        try:
            # CPU
            cpu_data = metrics.get("cpu", {})
            self.cpu_widget.set_value(cpu_data.get("usage_percent", 0))
            
            # Memory
            memory_data = metrics.get("memory", {})
            self.ram_widget.set_value(memory_data.get("percentage", 0))
            
            # GPU (prioritize most active GPU)
            gpu_data = metrics.get("gpu", [])
            if gpu_data:
                # Find the most active GPU (highest utilization or temperature)
                active_gpu = max(gpu_data, key=lambda x: (
                    x.get("utilization_gpu", 0),     # Prioritize by utilization
                    x.get("temperature", 0),         # Then by temperature
                    x.get("is_discrete", False),     # Prefer discrete GPUs
                    -gpu_data.index(x)               # Fallback to first in list
                ))
                
                gpu_util = active_gpu.get("utilization_gpu", 0)
                self.gpu_widget.set_value(gpu_util)
                
                # Debug output to help identify issues
                if hasattr(self, 'debug_mode') and self.debug_mode:
                    print(f"GPU Update: {active_gpu.get('name', 'Unknown')} - {gpu_util}% utilization")
            else:
                self.gpu_widget.set_value(0)
            
            # Temperature with enhanced display
            temp_data = metrics.get("temperature", {})
            summary = temp_data.get("summary", {})
            
            # Use CPU temperature as primary, fallback to highest temp
            cpu_temp = summary.get("cpu_temp", 0)
            if cpu_temp == 0:
                cpu_temp = summary.get("highest_temp", 0)
            
            self.temp_widget.set_value(cpu_temp)
            
            # Update temperature color based on ranges
            if cpu_temp > 0:
                if cpu_temp < 50:
                    self.temp_widget.set_color("#00ff00")  # Green (cool)
                elif cpu_temp < 65:
                    self.temp_widget.set_color("#ffff00")  # Yellow (warm)
                elif cpu_temp < 80:
                    self.temp_widget.set_color("#ff8000")  # Orange (hot)
                else:
                    self.temp_widget.set_color("#ff0000")  # Red (critical)
            
            # Store additional temperature data for detailed view
            self.temp_widget.detailed_data = temp_data
            
            # Update tooltip with detailed temperature info
            if temp_data and temp_data.get("sensors"):
                tooltip_text = "Temperature Sensors:\n"
                sensors = temp_data.get("sensors", {})
                for sensor_name, sensor_list in sensors.items():
                    for sensor in sensor_list:
                        temp = sensor.get("current", 0)
                        label = sensor.get("label", "Unknown")
                        tooltip_text += f"• {sensor_name} ({label}): {temp:.1f}°C\n"
                
                # Add critical warnings
                critical_sensors = temp_data.get("summary", {}).get("critical_sensors", [])
                if critical_sensors:
                    tooltip_text += "\n⚠️ CRITICAL TEMPERATURES:\n"
                    for sensor in critical_sensors:
                        tooltip_text += f"• {sensor['sensor']}: {sensor['temp']:.1f}°C\n"
                
                self.temp_widget.setToolTip(tooltip_text.strip())
            else:
                self.temp_widget.setToolTip("No temperature sensors detected")
            
            # Battery
            battery_data = metrics.get("battery")
            if battery_data:
                self.battery_widget.set_value(battery_data.get("percentage", 0))
                # Update color based on charge status with smooth transition
                if battery_data.get("plugged"):
                    self.battery_widget.set_color("#27ae60")  # Green when charging
                elif battery_data.get("percentage", 100) < 20:
                    self.battery_widget.set_color("#e74c3c")  # Red when low
                else:
                    self.battery_widget.set_color("#6c5ce7")  # Purple normally
            else:
                self.battery_widget.set_value(0)
            
            # FPS
            fps_data = metrics.get("fps", {})
            self.fps_widget.set_value(fps_data.get("current_fps", 0))
            
            # Handle gaming mode
            self.handle_gaming_mode(is_gaming)
            
        except Exception as e:
            print(f"Error updating metrics: {e}")

    def handle_gaming_mode(self, is_gaming):
        """Handle transition to/from gaming mode"""
        if is_gaming and not self._is_gaming_mode:
            self.enter_gaming_mode()
        elif not is_gaming and self._is_gaming_mode:
            self.exit_gaming_mode()

    def enter_gaming_mode(self):
        """Enter gaming mode with expanded layout"""
        self._is_gaming_mode = True
        
        # Show FPS widget if enabled
        metrics_config = self.config_manager.get_section("metrics")
        if metrics_config.get("show_fps", True):
            self.fps_widget.show()
        
        # Animate resize
        current_geometry = self.geometry()
        new_width = 500  # Wider for FPS widget
        new_geometry = QtCore.QRect(
            current_geometry.x(),
            current_geometry.y(),
            new_width,
            current_geometry.height()
        )
        
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(new_geometry)
        self.resize_animation.start()

    def exit_gaming_mode(self):
        """Exit gaming mode to compact layout"""
        self._is_gaming_mode = False
        
        # Hide FPS widget
        self.fps_widget.hide()
        
        # Animate resize
        current_geometry = self.geometry()
        new_width = 400  # Original width
        new_geometry = QtCore.QRect(
            current_geometry.x(),
            current_geometry.y(),
            new_width,
            current_geometry.height()
        )
        
        self.resize_animation.setStartValue(current_geometry)
        self.resize_animation.setEndValue(new_geometry)
        self.resize_animation.start()

    def toggle_click_through(self):
        """Toggle click-through mode"""
        hwnd = int(self.winId())
        if not self._click_through:
            make_click_through(hwnd)
            self._click_through = True
        else:
            remove_click_through(hwnd)
            self._click_through = False

    def dock_to_side(self, side):
        """Dock overlay to screen edge or corner"""
        self._dock_side = side
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        
        # Calculate margins
        margin = 10
        taskbar_height = 40  # Approximate taskbar height
        
        if side == "center":
            self.move(
                screen.width() // 2 - self.width() // 2,
                screen.height() // 2 - self.height() // 2
            )
        elif side == "left":
            self.move(margin, screen.height() // 2 - self.height() // 2)
        elif side == "right":
            self.move(screen.width() - self.width() - margin, screen.height() // 2 - self.height() // 2)
        elif side == "top":
            self.move(screen.width() // 2 - self.width() // 2, margin)
        elif side == "top-left":
            self.move(margin, margin)
        elif side == "top-right":
            self.move(screen.width() - self.width() - margin, margin)
        elif side == "bottom":
            self.move(screen.width() // 2 - self.width() // 2, screen.height() - self.height() - taskbar_height)
        elif side == "bottom-left":
            self.move(margin, screen.height() - self.height() - taskbar_height)
        elif side == "bottom-right":
            self.move(
                screen.width() - self.width() - margin,
                screen.height() - self.height() - taskbar_height
            )
        
        # Save dock preference
        self.config_manager.set_setting("overlay.dock_side", side)

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick docking"""
        # Ctrl+Num shortcuts for docking positions
        shortcuts = {
            # Number pad layout mapping
            QtCore.Qt.Key.Key_1: "bottom-left",    # 1 -> bottom-left
            QtCore.Qt.Key.Key_2: "bottom",         # 2 -> bottom
            QtCore.Qt.Key.Key_3: "bottom-right",   # 3 -> bottom-right
            QtCore.Qt.Key.Key_4: "left",           # 4 -> left
            QtCore.Qt.Key.Key_5: "center",         # 5 -> center
            QtCore.Qt.Key.Key_6: "right",          # 6 -> right
            QtCore.Qt.Key.Key_7: "top-left",       # 7 -> top-left
            QtCore.Qt.Key.Key_8: "top",            # 8 -> top
            QtCore.Qt.Key.Key_9: "top-right",      # 9 -> top-right
            QtCore.Qt.Key.Key_0: "none"            # 0 -> undock
        }
        
        for key, dock_side in shortcuts.items():
            shortcut = QtGui.QShortcut(
                QtGui.QKeySequence(QtCore.Qt.Modifier.CTRL | key), 
                self
            )
            shortcut.activated.connect(lambda side=dock_side: self.dock_to_side(side))

    def check_auto_hide(self):
        """Check if overlay should auto-hide based on fullscreen applications"""
        # This is a placeholder - would need platform-specific implementation
        pass

    @QtCore.pyqtSlot(str, object)
    def update_config(self, setting_path, value):
        """Handle configuration updates"""
        if setting_path.startswith("theme."):
            self.load_theme()
        elif setting_path == "overlay.opacity":
            self.setWindowOpacity(value)
        elif setting_path.startswith("metrics.show_"):
            self.update_widget_visibility()

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if (event.buttons() == QtCore.Qt.MouseButton.LeftButton and 
            self._drag_pos is not None and 
            not self._click_through):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            self._dock_side = "none"  # Undock when moved manually

    def enterEvent(self, event):
        """Handle mouse enter - fade in"""
        if self.windowOpacity() < 0.9:
            self.fade_animation.setStartValue(self.windowOpacity())
            self.fade_animation.setEndValue(0.9)
            self.fade_animation.start()

    def leaveEvent(self, event):
        """Handle mouse leave - fade out slightly"""
        if not self._is_gaming_mode:
            self.fade_animation.setStartValue(self.windowOpacity())
            self.fade_animation.setEndValue(0.7)
            self.fade_animation.start()

    def paintEvent(self, event):
        """Custom paint event for background"""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        
        # Background with rounded corners and gradient
        rect = self.rect()
        
        # Create gradient
        gradient = QtGui.QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QtGui.QColor(30, 30, 30, 200))
        gradient.setColorAt(1, QtGui.QColor(20, 20, 20, 220))
        
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60, 150), 1))
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
        
        # Add subtle inner highlight
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 30), 1))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 11, 11)
        
        # Add docking indicator if docked
        if hasattr(self, '_dock_side') and self._dock_side != "none":
            dock_color = QtGui.QColor("#007acc")
            dock_color.setAlpha(80)
            painter.setPen(QtGui.QPen(dock_color, 2))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 12, 12)
