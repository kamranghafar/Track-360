#!/bin/bash
# Portable Dashboard Startup Script for Linux/Mac
# Run this script to start the dashboard

echo "============================================================"
echo "    Dashboard Startup Script"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "No virtual environment found. Using system Python..."
fi

# Run the Python startup script
python3 start_dashboard.py
