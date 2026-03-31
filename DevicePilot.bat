@echo off
title DevicePilot Launcher
cls

echo.
echo ===================================
echo      DevicePilot System Monitor
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Starting DevicePilot...
echo.

REM Run the launcher
python launch_devicepilot.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo DevicePilot exited with an error.
    pause
)

exit /b 0
