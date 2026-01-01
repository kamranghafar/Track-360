import os
import subprocess
import sys

def run_migrations():
    """
    Run all pending Django migrations.
    """
    print("Starting migration process...")
    
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to manage.py
    manage_py = os.path.join(current_dir, 'manage.py')
    
    # Check if manage.py exists
    if not os.path.exists(manage_py):
        print(f"Error: manage.py not found at {manage_py}")
        return False
    
    try:
        # Run the migrate command
        print("Running migrations...")
        result = subprocess.run(
            [sys.executable, manage_py, 'migrate'],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Print the output
        print("Migration output:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        
        print("Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        print("Command output:")
        print(e.stdout)
        print("Error output:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    run_migrations()