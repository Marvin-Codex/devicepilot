#!/usr/bin/env python3
"""
DevicePilot Application Launcher
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devicepilot.main import DevicePilotApp


def main():
    """Main entry point"""
    app = DevicePilotApp()
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nShutting down DevicePilot...")
        app.running = False
        sys.exit(0)


if __name__ == "__main__":
    main()
