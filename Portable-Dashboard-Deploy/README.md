# Portable Dashboard Deployment - Protected Distribution v2.0

This is a portable, ready-to-deploy **protected version** of the Dashboard project with **compile-on-install** for cross-version compatibility. Everything you need is contained in this folder, including the database.

**IMPORTANT**: This distribution includes source code that is automatically compiled during setup for YOUR specific Python version. After setup, you can optionally remove the source files for intellectual property protection.

## Quick Start

### Windows Users
1. **First Time Setup**: Double-click `setup.bat`
2. **Start Dashboard**: Double-click `start_dashboard.bat`

### Linux/Mac Users
1. **First Time Setup**: Run `./setup.sh` or `bash setup.sh`
2. **Start Dashboard**: Run `./start_dashboard.sh` or `bash start_dashboard.sh`

### Using Python Directly
1. **First Time Setup**: `python setup.py` (or `python3 setup.py`)
2. **Start Dashboard**: `python start_dashboard.py` (or `python3 start_dashboard.py`)

## What Happens When You Start?

When you run the startup script, you'll be prompted for:
1. **IP Address**:
   - Enter `0.0.0.0` to allow connections from any device on your network
   - Enter `127.0.0.1` or `localhost` for local access only
   - Press Enter to use default (0.0.0.0)

2. **Port Number**:
   - Enter any available port (e.g., 8000, 8080, 3000)
   - Press Enter to use default (8000)

The dashboard will then start and display the URL to access it.

## System Requirements

- **Python**: Version 3.8 or higher
- **Operating System**: Windows, Linux, or macOS
- **RAM**: At least 2GB recommended (4GB+ if using AI features)
- **Disk Space**: At least 500MB free space

## First-Time Setup Details

The setup script will:
1. Check your Python version
2. Optionally create a virtual environment (recommended)
3. Install all required dependencies
4. Create/migrate the database if needed
5. Optionally create an admin user

## Folder Structure

```
Portable-Dashboard-Deploy/
├── dashboard/              # Main dashboard application
├── dashboard_project/      # Django project settings
├── ai_agent/              # AI assistant features
├── db.sqlite3             # Database (contains all your data)
├── requirements.txt       # Python dependencies
├── manage.py              # Django management script
├── setup.py               # First-time setup script
├── setup.bat              # Windows setup launcher
├── setup.sh               # Linux/Mac setup launcher
├── start_dashboard.py     # Dashboard startup script
├── start_dashboard.bat    # Windows startup launcher
├── start_dashboard.sh     # Linux/Mac startup launcher
└── README.md              # This file
```

## Deployment to Another System

To deploy this dashboard on another computer:

1. **Copy the entire folder** to the new system
2. Make sure **Python 3.8+** is installed
3. Run the **setup script** for first-time installation
4. Run the **startup script** to launch the dashboard

**Important**: Keep the `db.sqlite3` file if you want to preserve your data!

## Database Location

The database (`db.sqlite3`) is located in the same directory as the scripts. When you copy this folder to another system, the database goes with it, preserving all your data.

## Accessing the Dashboard

After starting the dashboard:

- **Local Access**: http://127.0.0.1:PORT
- **Network Access**: http://YOUR_IP:PORT
  - To find your IP:
    - Windows: Run `ipconfig` in Command Prompt
    - Linux/Mac: Run `ifconfig` or `ip addr` in Terminal

## Troubleshooting

### Port Already in Use
If you see "port already in use" error:
- Choose a different port when prompted
- Or stop the application using that port

### Python Not Found
- Make sure Python is installed
- On Windows, check "Add Python to PATH" during installation
- On Linux/Mac, use your package manager (apt, yum, brew)

### Dependencies Installation Fails
- Check your internet connection
- Try running: `pip install -r requirements.txt` manually
- On Linux/Mac, you might need: `pip3 install -r requirements.txt`

### Database Errors
- If database is corrupted, delete `db.sqlite3` and run setup again
- This will create a fresh database (you'll lose data)

### Permission Denied (Linux/Mac)
- Make scripts executable: `chmod +x *.sh *.py`

## Managing the Dashboard

### Creating an Admin User
```bash
python manage.py createsuperuser
```

### Running Migrations
```bash
python manage.py migrate
```

### Collecting Static Files (if needed)
```bash
python manage.py collectstatic
```

## Virtual Environment

The setup script offers to create a virtual environment (`.venv` folder). This is recommended as it:
- Keeps dependencies isolated
- Prevents conflicts with other Python projects
- Makes the deployment more portable

If you use a virtual environment:
- **Windows**: It's automatically activated by the `.bat` scripts
- **Linux/Mac**: It's automatically activated by the `.sh` scripts

## Cross-Version Compatible Protection

This package uses a **compile-on-install** approach:
- Source code is included in the distribution
- During setup, code is compiled for YOUR specific Python version
- After compilation, you can OPTIONALLY remove source files for protection
- Works with ANY Python 3.8+ version (3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14+)
- No "bad magic number" errors across Python versions!

**Setup will ask**: "Remove source files? (yes/no)"
- YES = Source code removed after compilation (protected distribution)
- NO = Source code kept (easier debugging, still fully functional)

**Note**: Python bytecode provides basic code protection. For enterprise-level security, consider PyInstaller, Nuitka, or PyArmor.

## Security Notes

- The included `SECRET_KEY` in settings is for development only
- For production use, generate a new secret key
- The database contains user data - keep it secure
- Don't expose the dashboard to the internet without proper security measures
- This binary distribution protects intellectual property but is not enterprise-level encryption

## Support

For issues or questions about this deployment package, refer to:
- The main project documentation
- Django documentation: https://docs.djangoproject.com/

## Features

This dashboard includes:
- Project management
- Resource planning
- KPI tracking
- Automation metrics
- AI-powered chat assistant
- Weekly meeting management
- Product documentation
- And more...

---

**Happy Dashboard Management!**
