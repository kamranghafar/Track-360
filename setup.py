#!/usr/bin/env python
"""
First-time Setup Script for Portable Dashboard
This script will help you set up the environment for the first time.
"""
import os
import sys
import subprocess
import py_compile
import shutil
from pathlib import Path

def compile_source_code(base_path):
    """Compile all Python source files to bytecode for current Python version"""
    print("\n" + "=" * 70)
    print("COMPILING APPLICATION FOR YOUR PYTHON VERSION")
    print("=" * 70)
    print(f"Your Python: {sys.version.split()[0]}")
    print("\nThis ensures compatibility with your specific Python version...")
    print()

    compiled_count = 0
    app_dirs = ['dashboard', 'ai_agent', 'dashboard_project']

    for app_dir in app_dirs:
        app_path = base_path / app_dir
        if not app_path.exists():
            continue

        print(f"Compiling {app_dir}/...")

        for root, dirs, files in os.walk(app_path):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                if file.endswith('.py'):
                    py_file = os.path.join(root, file)
                    try:
                        py_compile.compile(py_file, cfile=py_file + 'c', doraise=True)
                        compiled_count += 1
                    except Exception as e:
                        print(f"  Warning: Could not compile {py_file}: {e}")

    print(f"\n✓ Compiled {compiled_count} Python files for your system")
    return compiled_count

def remove_source_files(base_path):
    """Remove .py source files, keeping only .pyc bytecode"""
    print("\n" + "=" * 70)
    print("SOURCE CODE PROTECTION")
    print("=" * 70)
    print("\nWould you like to remove source code files (.py) and keep only")
    print("compiled bytecode (.pyc) for intellectual property protection?")
    print()
    print("  YES - Remove source files (recommended for distribution)")
    print("  NO  - Keep source files (easier for debugging/development)")
    print()

    choice = input("Remove source files? (yes/no) [default: no]: ").strip().lower()

    if choice not in ['yes', 'y']:
        print("\nSource files kept. Application will run normally.")
        return False

    print("\nRemoving source files...")
    removed_count = 0
    app_dirs = ['dashboard', 'ai_agent', 'dashboard_project']

    for app_dir in app_dirs:
        app_path = base_path / app_dir
        if not app_path.exists():
            continue

        for root, dirs, files in os.walk(app_path):
            # Skip __pycache__ directories
            if '__pycache__' in root:
                continue

            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    py_file = os.path.join(root, file)
                    pyc_file = py_file + 'c'

                    # Only remove if corresponding .pyc exists
                    if os.path.exists(pyc_file):
                        try:
                            os.remove(py_file)
                            removed_count += 1
                        except Exception as e:
                            print(f"  Warning: Could not remove {py_file}: {e}")

    # Remove __pycache__ directories
    for app_dir in app_dirs:
        app_path = base_path / app_dir
        if app_path.exists():
            for root, dirs, files in os.walk(app_path, topdown=False):
                for dir_name in dirs:
                    if dir_name == '__pycache__':
                        try:
                            shutil.rmtree(os.path.join(root, dir_name))
                        except Exception:
                            pass

    print(f"✓ Removed {removed_count} source files")
    print("✓ Source code is now protected (bytecode only)")
    return True

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

    venv_python = sys.executable  # Default to current Python

    if create_venv in ['yes', 'y']:
        venv_path = current_dir / '.venv'
        if venv_path.exists():
            print("Virtual environment already exists.")
            # Determine the correct Python executable in venv
            if os.name == 'nt':  # Windows
                venv_python = venv_path / 'Scripts' / 'python.exe'
            else:  # Unix-like
                venv_python = venv_path / 'bin' / 'python'
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

    # Compile source code for current Python version
    compiled_count = compile_source_code(current_dir)

    if compiled_count > 0:
        # Ask if user wants to remove source files
        source_removed = remove_source_files(current_dir)
    else:
        print("Warning: No files were compiled.")
        source_removed = False

    # Check if database exists
    db_path = current_dir / 'db.sqlite3'
    if not db_path.exists():
        print("\n" + "=" * 70)
        print("DATABASE SETUP")
        print("=" * 70)
        print("\nNo database found.")
        create_db = input("Do you want to create a new database? (yes/no): ").strip().lower()
        if create_db in ['yes', 'y']:
            print("\nRunning migrations to create database...")
            try:
                subprocess.run([str(venv_python), 'manage.py', 'migrate'], check=True)
                print("Database created successfully!")

                # Ask about creating superuser
                print("\nWould you like to create an admin user?")
                create_admin = input("Create admin user? (yes/no): ").strip().lower()
                if create_admin in ['yes', 'y']:
                    subprocess.run([str(venv_python), 'manage.py', 'createsuperuser'])

            except subprocess.CalledProcessError as e:
                print(f"Error creating database: {e}")
                return
    else:
        print("\n✓ Database already exists - skipping database creation.")

    print("\n" + "=" * 70)
    print("    Setup Complete!")
    print("=" * 70)

    if source_removed:
        print("\n✓ Application compiled for Python", sys.version.split()[0])
        print("✓ Source code removed - bytecode protected")
        print("✓ Dependencies installed")
        print("✓ Ready to deploy!")
    else:
        print("\n✓ Application compiled for Python", sys.version.split()[0])
        print("✓ Source code preserved")
        print("✓ Dependencies installed")
        print("✓ Ready to run!")

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
