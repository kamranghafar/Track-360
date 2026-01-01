import subprocess
import sys

def install_dependencies():
    """Install the required dependencies for MCP"""
    dependencies = [
        "jsonschema",
        "httpx_sse",
        "pywin32",
        "pydantic_settings",
        "starlette",
        "sse_starlette"
    ]
    
    print("Installing MCP dependencies...")
    for dependency in dependencies:
        print(f"Installing {dependency}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
            print(f"Successfully installed {dependency}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {dependency}: {str(e)}")
    
    print("All dependencies installed successfully!")

if __name__ == "__main__":
    install_dependencies()