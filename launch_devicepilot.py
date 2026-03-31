#!/usr/bin/env python3
"""
DevicePilot Launcher Script
Handles installation, dependency checking, and application startup
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True


def check_dependencies():
    """Check and install required dependencies"""
    requirements = [
        'PyQt6',
        'psutil',
        'nvidia-ml-py',
        'pywin32',
        'Pillow',
        'requests'
    ]
    
    missing_deps = []
    
    for req in requirements:
        try:
            if req == 'PyQt6':
                import PyQt6.QtWidgets
            elif req == 'psutil':
                import psutil
            elif req == 'nvidia-ml-py':
                import pynvml
            elif req == 'pywin32':
                import win32com.client
            elif req == 'Pillow':
                import PIL
            elif req == 'requests':
                import requests
            
            print(f"✅ {req} is installed")
            
        except ImportError:
            print(f"❌ {req} is missing")
            missing_deps.append(req)
    
    if missing_deps:
        print(f"\n🔧 Installing missing dependencies: {', '.join(missing_deps)}")
        return install_dependencies(missing_deps)
    
    return True


def install_dependencies(deps):
    """Install missing dependencies using pip"""
    try:
        for dep in deps:
            print(f"Installing {dep}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.returncode == 0:
                print(f"✅ {dep} installed successfully")
            else:
                print(f"❌ Failed to install {dep}")
                print(f"Error: {result.stderr}")
                return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def check_admin_privileges():
    """Check if running with administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def create_desktop_shortcut():
    """Create desktop shortcut for easy access"""
    try:
        import win32com.client
        
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / "DevicePilot.lnk"
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{Path(__file__).parent / "devicepilot" / "main.py"}"'
        shortcut.WorkingDirectory = str(Path(__file__).parent)
        shortcut.IconLocation = sys.executable
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not create desktop shortcut: {e}")
        return False


def setup_startup_registry():
    """Add to Windows startup registry (optional)"""
    try:
        import winreg
        
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        app_path = f'"{sys.executable}" "{Path(__file__).parent / "devicepilot" / "main.py"}"'
        winreg.SetValueEx(key, "DevicePilot", 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
        
        print("✅ Added to Windows startup")
        return True
        
    except Exception as e:
        print(f"⚠️ Could not add to startup: {e}")
        return False


def main():
    """Main launcher function"""
    print("🚀 DevicePilot Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return False
    
    print()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        input("Press Enter to exit...")
        return False
    
    print()
    
    # Check admin privileges
    is_admin = check_admin_privileges()
    if is_admin:
        print("👑 Running with administrator privileges")
    else:
        print("👤 Running with standard user privileges")
        print("   (Some advanced features may be limited)")
    
    print()
    
    # Offer to create shortcuts and startup entry
    try:
        while True:
            choice = input("Create desktop shortcut? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                create_desktop_shortcut()
                break
            elif choice in ['n', 'no']:
                break
            else:
                print("Please enter 'y' or 'n'")
        
        while True:
            choice = input("Add to Windows startup? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                setup_startup_registry()
                break
            elif choice in ['n', 'no']:
                break
            else:
                print("Please enter 'y' or 'n'")
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
    
    print()
    print("🎯 Starting DevicePilot...")
    
    # Change to devicepilot directory and run main.py
    try:
        devicepilot_path = Path(__file__).parent / "devicepilot"
        
        # Add the parent directory to Python path so we can import devicepilot package
        parent_path = str(Path(__file__).parent)
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)
        
        # Change to the devicepilot directory
        original_cwd = os.getcwd()
        os.chdir(devicepilot_path)
        
        # Import and run the main application
        from devicepilot.main import main as app_main
        
        result = app_main()
        
        # Restore original directory
        os.chdir(original_cwd)
        
        return result
        
    except Exception as e:
        print(f"❌ Error starting DevicePilot: {e}")
        import traceback
        print("Full error details:")
        traceback.print_exc()
        print("\nMake sure all files are present and try again.")
        input("Press Enter to exit...")
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 DevicePilot launcher interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
