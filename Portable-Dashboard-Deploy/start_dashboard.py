#!/usr/bin/env python
"""
Portable Dashboard Startup Script
This script will prompt for IP and port, then start the Django dashboard.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("    Dashboard Startup Script")
    print("=" * 60)
    print()

    # Get current directory
    current_dir = Path(__file__).resolve().parent
    os.chdir(current_dir)

    # Check if database exists
    db_path = current_dir / 'db.sqlite3'
    if not db_path.exists():
        print("WARNING: Database file not found!")
        print("A new database will be created.")
        print("You may need to run migrations.")
        print()
        create_db = input("Do you want to create a new database? (yes/no): ").strip().lower()
        if create_db in ['yes', 'y']:
            print("\nRunning migrations...")
            try:
                subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
                print("Database created successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error creating database: {e}")
                return
        else:
            print("Cannot start without a database. Exiting...")
            return

    # Prompt for IP address
    print("\nEnter the IP address to bind to:")
    print("  - Use '0.0.0.0' to allow external connections")
    print("  - Use '127.0.0.1' or 'localhost' for local only")
    ip_address = input("IP Address (default: 0.0.0.0): ").strip()
    if not ip_address:
        ip_address = "0.0.0.0"

    # Prompt for port
    print("\nEnter the port number:")
    port = input("Port (default: 8000): ").strip()
    if not port:
        port = "8000"

    # Validate port
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            print("Error: Port must be between 1 and 65535")
            return
    except ValueError:
        print("Error: Port must be a number")
        return

    print("\n" + "=" * 60)
    print(f"Starting Django Dashboard on {ip_address}:{port}")
    print("=" * 60)
    print("\nAccess the dashboard at:")
    if ip_address == "0.0.0.0":
        print(f"  - Local: http://127.0.0.1:{port}")
        print(f"  - Network: http://<your-ip>:{port}")
    else:
        print(f"  - http://{ip_address}:{port}")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    print()

    # Set environment variable for settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')

    # Start Django server
    try:
        subprocess.run([
            sys.executable,
            'manage.py',
            'runserver',
            f'{ip_address}:{port}',
            '--noreload'
        ])
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        print("Dashboard stopped.")
    except Exception as e:
        print(f"\nError starting server: {e}")
        return

if __name__ == '__main__':
    main()
