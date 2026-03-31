# OpenHardwareMonitorLib.dll Setup

This folder should contain the OpenHardwareMonitorLib.dll file for accurate hardware monitoring.

## Download Instructions:

1. Go to: https://github.com/openhardwaremonitor/openhardwaremonitor
2. Download the latest release
3. Extract the zip file
4. Copy `OpenHardwareMonitorLib.dll` from the extracted folder
5. Place it in this `libs/` directory

## Required Python Package:

Make sure you have pythonnet installed:
```bash
pip install pythonnet
```

## File Structure Should Be:
```
UtilityApp/
├── libs/
│   └── OpenHardwareMonitorLib.dll  ← Place the DLL here
├── devicepilot/
│   └── core/
│       └── hardware_monitor.py
└── ...
```

Once the DLL is in place, the application will use it for accurate hardware monitoring including:
- CPU temperatures (all cores)
- GPU temperatures (NVIDIA/AMD)
- Motherboard sensors
- Fan speeds
- Power consumption
- Voltage readings

Without this DLL, the application will fall back to basic WMI/psutil monitoring.
