#!/bin/bash
# First-time Setup Script for Linux/Mac
# Run this script to set up the dashboard

echo "======================================================================"
echo "    Dashboard First-Time Setup"
echo "======================================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Run the Python setup script
python3 setup.py
