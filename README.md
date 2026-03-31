# DevicePilot - Professional System Monitoring Overlay

![DevicePilot Logo](https://img.shields.io/badge/DevicePilot-v1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Overview

DevicePilot is a professional, feature-rich system monitoring overlay for Windows that provides real-time hardware metrics with a beautiful, transparent interface. Designed for gamers, developers, and power users who need constant visibility into their system's performance.

### ✨ Key Features

- **🎮 Gaming Mode**: Automatic detection of gaming applications with expanded FPS monitoring
- **🔧 Comprehensive Metrics**: CPU, RAM, GPU, Temperature, Battery, and FPS monitoring
- **🎨 Professional Design**: Modern, transparent overlay with multiple themes
- **📱 Dockable Interface**: Dock to any screen edge or keep floating
- **⚙️ Extensive Configuration**: Per-app profiles, custom themes, and behavior settings
- **🔋 Battery Health**: Detailed battery analysis and health recommendations
- **📊 Advanced Analytics**: Historical data, performance trends, and detailed reports
- **🖱️ Smart Interactions**: Click-through mode, auto-hide, and contextual controls

## 📸 Screenshots

### Main Overlay
- **Idle Mode**: Compact display showing essential metrics
- **Gaming Mode**: Expanded view with FPS and detailed GPU information
- **Docked Mode**: Clean edge-docked interface

### Settings Interface
- **Professional UI**: Dark theme with organized tabs
- **Gaming Profiles**: Process detection and per-app settings
- **Theme Customization**: Colors, opacity, and visual effects

### Battery Health Monitor
- **Health Analysis**: Comprehensive battery health scoring
- **Detailed Reports**: Design capacity, cycle count, usage patterns
- **Care Recommendations**: Personalized tips for battery longevity

## 🛠️ Installation

### Quick Start

1. **Download or Clone** the repository:
   ```bash
   git clone https://github.com/Marvin-Codex/devicepilot.git
   cd devicepilot
   ```

2. **Run the Launcher** (recommended):
   ```bash
   python launch_devicepilot.py
   ```
   The launcher will automatically:
   - Check Python version compatibility
   - Install missing dependencies
   - Offer to create shortcuts
   - Start the application

3. **Alternative - Manual Setup**:
   ```bash
   pip install -r requirements.txt
   cd devicepilot
   python main.py
   ```

### System Requirements

- **OS**: Windows 10/11 (64-bit recommended)
- **Python**: 3.8 or higher
- **RAM**: 100MB minimum
- **CPU**: Minimal impact (<1% CPU usage)

### Dependencies

- `PyQt6` - Modern GUI framework
- `psutil` - System metrics collection
- `py3nvml` - NVIDIA GPU monitoring
- `pywin32` - Windows API integration
- `Pillow` - Image processing
- `requests` - Network operations

## 📋 Usage Guide

### First Time Setup

1. **Launch DevicePilot** using the launcher or main.py
2. **System Tray**: Look for the DevicePilot icon in the system tray
3. **Initial Configuration**: Right-click the tray icon → Settings
4. **Gaming Setup**: Add your gaming processes in Gaming tab
5. **Positioning**: Drag the overlay to your preferred location

### Basic Controls

| Action | Method |
|--------|---------|
| **Move Overlay** | Left-click and drag |
| **Context Menu** | Right-click on overlay |
| **Toggle Visibility** | Double-click tray icon |
| **Settings** | Tray icon → Settings |
| **Battery Health** | Tray icon → Battery Health |
| **Click-through** | Context menu → Toggle Click-through |

### Gaming Mode

Gaming mode automatically activates when DevicePilot detects gaming applications:

- **Expanded Display**: Shows FPS alongside other metrics
- **Enhanced Monitoring**: Higher update frequency
- **Gaming-specific UI**: Optimized layout for gaming

**Adding Games**: Settings → Gaming → Add Process
- Use exact executable names (e.g., `game.exe`)
- Wildcards supported (e.g., `*.exe`)
- Common launchers pre-configured

### Themes and Customization

#### Built-in Themes
- **Modern Dark**: Professional dark theme with blue accents
- **Modern Light**: Clean light theme
- **Minimal**: Simplified, distraction-free design
- **Gaming**: High-contrast theme optimized for gaming

#### Custom Styling
- **Opacity Control**: 30% - 100% transparency
- **Border Radius**: Adjustable corner rounding
- **Shadow Effects**: Customizable drop shadows
- **Gradient Backgrounds**: Modern gradient overlays

### Docking System

DevicePilot supports intelligent docking to screen edges:

- **Auto-snap**: Automatically snaps to edges when dragged close
- **Edge Docking**: Left, Right, Top, or Bottom edge docking
- **Smart Positioning**: Avoids taskbar and system UI elements
- **Multi-monitor**: Works across multiple displays

## 🔧 Advanced Configuration

### Configuration File

Settings are stored in `devicepilot/settings/config.json`:

```json
{
  "overlay": {
    "opacity": 0.9,
    "dock_side": "none",
    "click_through": false
  },
  "metrics": {
    "update_interval": 1.0,
    "show_fps": true,
    "temperature_unit": "C"
  },
  "profiles": {
    "gaming_mode_enabled": true,
    "gaming_processes": ["game.exe"]
  }
}
```

### Per-Application Profiles

Create custom settings for specific applications:

1. **Settings** → **Gaming** → **Add Process**
2. Configure overlay behavior per game
3. Automatic activation when game launches

### FPS Monitoring

DevicePilot supports multiple FPS detection methods:

1. **RTSS Integration**: Best accuracy (requires MSI Afterburner/RTSS)
2. **DirectX Hooking**: Advanced method (requires admin privileges)
3. **Performance Counters**: Windows built-in counters
4. **GPU-based Estimation**: Fallback method using GPU patterns

### Battery Monitoring

Comprehensive battery analysis includes:

- **Health Scoring**: Percentage-based health assessment
- **Cycle Count Tracking**: Battery wear analysis
- **Capacity Analysis**: Design vs. current capacity comparison
- **Usage Patterns**: Charging behavior insights
- **Care Recommendations**: Personalized maintenance tips

## 🎯 Performance Impact

DevicePilot is designed for minimal system impact:

| Metric | Impact |
|--------|--------|
| **CPU Usage** | <1% average |
| **RAM Usage** | ~50-100MB |
| **GPU Impact** | Negligible |
| **Battery Impact** | <1% additional drain |
| **Network Usage** | None (offline operation) |

## 🚨 Troubleshooting

### Common Issues

#### Overlay Not Visible
- Check if overlay is hidden (double-click tray icon)
- Verify opacity settings (not set to fully transparent)
- Ensure "Always on Top" is enabled

#### No GPU Metrics
- **NVIDIA**: Install latest drivers and py3nvml package
- **AMD**: Requires Windows Performance Toolkit or OpenHardwareMonitor
- **Intel**: Limited support through Windows APIs

#### FPS Not Detecting
- Install MSI Afterburner with RTSS for best results
- Add specific game processes to gaming list
- Run as administrator for advanced detection methods

#### Battery Health Unavailable
- Feature requires Windows 10/11
- Some older laptops may not support detailed battery reporting
- Run as administrator for enhanced battery features

### Performance Issues

#### High CPU Usage
- Increase update interval in Settings → Metrics
- Disable unnecessary metrics
- Check for conflicting software

#### Memory Leaks
- Restart DevicePilot if memory usage grows over time
- Check for corrupted configuration files
- Update to latest version

### Getting Help

1. **Check Documentation**: Review this README and in-app help
2. **Configuration Reset**: Settings → Reset to Defaults
3. **Log Files**: Enable logging in Advanced settings
4. **Issue Reports**: Submit detailed issue reports with logs

## 🔮 Advanced Features

### Command Line Arguments

DevicePilot supports several command line options:

```bash
python main.py --help                 # Show help
python main.py --minimized           # Start minimized
python main.py --admin               # Request admin privileges
python main.py --config=custom.json  # Use custom config
python main.py --debug               # Enable debug mode
```

### API Integration

DevicePilot exposes a simple API for third-party integration:

```python
# Example: Get current metrics
from devicepilot.core.metrics import MetricsCollector

collector = MetricsCollector()
metrics = collector.get_all_metrics()
print(f"CPU: {metrics['cpu']['usage_percent']}%")
```

### Plugin System (Future)

Planned plugin architecture will support:
- Custom metric sources
- Additional overlay widgets
- Third-party hardware integration
- Export to external monitoring systems

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/yourusername/devicepilot.git
   cd devicepilot
   ```

2. **Development Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Run Tests**:
   ```bash
   python -m pytest tests/
   ```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Document all public functions
- Include unit tests for new features

### Pull Request Process

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Make changes with tests
3. Update documentation
4. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt6**: Excellent GUI framework
- **psutil**: Cross-platform system monitoring
- **NVIDIA**: NVML library for GPU monitoring
- **Microsoft**: Windows APIs and documentation
- **Community**: User feedback and contributions

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/devicepilot/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/devicepilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/devicepilot/discussions)

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Network monitoring (bandwidth, connections)
- [ ] Disk I/O monitoring
- [ ] Custom alerts and notifications
- [ ] Export data to CSV/JSON
- [ ] Multiple overlay instances

### Version 1.2 (Planned)
- [ ] Plugin system
- [ ] Web dashboard
- [ ] Remote monitoring
- [ ] Mobile companion app
- [ ] Advanced analytics

### Version 2.0 (Future)
- [ ] Cross-platform support (macOS, Linux)
- [ ] Cloud sync
- [ ] AI-powered insights
- [ ] VR/AR integration
- [ ] Professional enterprise features

---

**DevicePilot** - *Professional System Monitoring, Perfected.*

Made with ❤️ for the Windows community

© 2026 Sserunjoji Marvin
