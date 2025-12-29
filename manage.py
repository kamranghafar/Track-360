#!/usr/bin/env python
"""Dashboard Runtime - Binary Distribution"""
import sys
import os

# Set up environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')

# Import and run Django
try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError("Django not installed. Run setup first.") from exc

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
