@echo off
REM First-time Setup Script for Windows
REM Double-click this file to set up the dashboard

echo ======================================================================
echo     Dashboard First-Time Setup
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Run the Python setup script
python setup.py

pause
