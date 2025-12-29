#!/usr/bin/env python
"""
First-time Setup Script for Portable Dashboard
This script will help you set up the environment for the first time.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 70)
    print("    Dashboard First-Time Setup")
    print("=" * 70)
    print()

    # Get current directory
    current_dir = Path(__file__).resolve().parent
    os.chdir(current_dir)

    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return

    print(f"Python version: {sys.version.split()[0]} - OK")
    print()

    # Ask about virtual environment
    print("It's recommended to use a virtual environment.")
    create_venv = input("Do you want to create a virtual environment? (yes/no): ").strip().lower()

    if create_venv in ['yes', 'y']:
        venv_path = current_dir / '.venv'
        if venv_path.exists():
            print("Virtual environment already exists.")
        else:
            print("\nCreating virtual environment...")
            try:
                subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
                print("Virtual environment created successfully!")

                # Determine the correct Python executable in venv
                if os.name == 'nt':  # Windows
                    venv_python = venv_path / 'Scripts' / 'python.exe'
                else:  # Unix-like
                    venv_python = venv_path / 'bin' / 'python'

                # Install dependencies
                print("\nInstalling dependencies...")
                subprocess.run([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
                subprocess.run([str(venv_python), '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
                print("Dependencies installed successfully!")

            except subprocess.CalledProcessError as e:
                print(f"Error during setup: {e}")
                return
    else:
        # Install dependencies using system Python
        print("\nInstalling dependencies with system Python...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("Dependencies installed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            return

    # Check if database exists
    db_path = current_dir / 'db.sqlite3'
    if not db_path.exists():
        print("\nNo database found.")
        create_db = input("Do you want to create a new database? (yes/no): ").strip().lower()
        if create_db in ['yes', 'y']:
            print("\nRunning migrations to create database...")
            try:
                if create_venv in ['yes', 'y'] and venv_python.exists():
                    subprocess.run([str(venv_python), 'manage.py', 'migrate'], check=True)
                else:
                    subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
                print("Database created successfully!")

                # Ask about creating superuser
                print("\nWould you like to create an admin user?")
                create_admin = input("Create admin user? (yes/no): ").strip().lower()
                if create_admin in ['yes', 'y']:
                    if create_venv in ['yes', 'y'] and venv_python.exists():
                        subprocess.run([str(venv_python), 'manage.py', 'createsuperuser'])
                    else:
                        subprocess.run([sys.executable, 'manage.py', 'createsuperuser'])

            except subprocess.CalledProcessError as e:
                print(f"Error creating database: {e}")
                return
    else:
        print("\nDatabase already exists - skipping database creation.")

    print("\n" + "=" * 70)
    print("    Setup Complete!")
    print("=" * 70)
    print("\nYou can now start the dashboard by running:")
    if os.name == 'nt':  # Windows
        print("  - Double-click 'start_dashboard.bat'")
        print("  - Or run: python start_dashboard.py")
    else:  # Unix-like
        print("  - Run: ./start_dashboard.sh")
        print("  - Or run: python3 start_dashboard.py")
    print()

if __name__ == '__main__':
    main()
