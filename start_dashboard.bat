@echo off
REM Portable Dashboard Startup Script for Windows
REM Double-click this file to start the dashboard

echo ============================================================
echo     Dashboard Startup Script
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Using system Python...
)

REM Run the Python startup script
python start_dashboard.py

pause
