# Track360 - Project Management Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.0+-green.svg)](https://www.djangoproject.com/)

A comprehensive project management dashboard built with Django, featuring resource planning, KPI tracking, quarter management, and an AI-powered assistant.

## Features

- **Project Management**: Track projects, tasks, and deliverables
- **Resource Planning**: Manage team members, allocations, and utilization
- **KPI Management**: Define, track, and rate Key Performance Indicators
- **Quarter Planning**: Set quarterly targets and track progress
- **Weekly Updates**: Product and project status tracking
- **Automation Tracking**: Monitor automation sprints and metrics
- **Production Bug Tracking**: Log and manage production issues
- **AI Assistant**: Built-in AI agent for intelligent assistance
- **Documentation Management**: Centralized product and department documentation
- **Roadmap Planning**: Track feature roadmaps with priorities
- **1-on-1 Feedback**: Schedule and document feedback sessions
- **SOPs Management**: Standard Operating Procedures tracking

## Prerequisites

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (comes with Python)

## Quick Start (Recommended for First-Time Users)

### Windows

```bash
# 1. Run setup
setup.bat

# 2. Start the dashboard
start_dashboard.bat
```

### Linux/Mac

```bash
# 1. Make scripts executable
chmod +x setup.sh start_dashboard.sh

# 2. Run setup
./setup.sh

# 3. Start the dashboard
./start_dashboard.sh
```

### Alternative (All Platforms)

```bash
# 1. Run setup
python setup.py

# 2. Start the dashboard
python start_dashboard.py
```

## Installation for Development

### 1. Clone the Repository

```bash
git clone https://github.com/Kamranghafar92/Track360.git
cd Track360/Portable-Dashboard-Deploy
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and set your configuration
# IMPORTANT: Generate a new SECRET_KEY for production!
```

### 5. Initialize Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The dashboard will be available at: http://127.0.0.1:8000

## Configuration

### Environment Variables

Create a .env file in the project root (copy from .env.example):

```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
```

**Security Note**: Always generate a new SECRET_KEY for production:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Usage

### Accessing the Dashboard

1. Start the server (see Quick Start above)
2. Open your browser and navigate to http://127.0.0.1:8000
3. Log in with your credentials (created during setup)

### Key Sections

- **Dashboard**: Overview of projects, resources, and KPIs
- **Projects**: Manage all your projects and tasks
- **Resources**: Team member allocation and planning
- **Quarters**: Set and track quarterly objectives
- **KPIs**: Define and monitor key metrics
- **Automation**: Track automation initiatives
- **Documentation**: Access product and department docs
- **AI Assistant**: Get intelligent help with your queries

## Deployment

### Production Deployment Checklist

- [ ] Set DJANGO_DEBUG=False in .env
- [ ] Generate new DJANGO_SECRET_KEY
- [ ] Configure DJANGO_ALLOWED_HOSTS with your domain
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure static files serving
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure backup strategy for database
- [ ] Review and update security settings

### Deploying to Another Computer

1. Copy the entire project folder to the new computer
2. Ensure Python 3.8+ is installed
3. Run setup script (setup.bat or setup.sh)
4. Copy your existing db.sqlite3 file (if migrating data)
5. Start the dashboard

## Project Structure

```
Track360/
├── dashboard/              # Main dashboard app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   ├── static/            # CSS, JS, images
│   └── templates/         # HTML templates
├── ai_agent/              # AI assistant app
├── dashboard_project/     # Django project settings
│   ├── settings.py        # Configuration
│   └── urls.py            # Root URL config
├── db.sqlite3             # SQLite database (not in git)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Dependencies

Main dependencies (see requirements.txt for complete list):

- **Django 5.0+** - Web framework
- **django-import-export** - Data import/export
- **pandas** - Data manipulation
- **openpyxl** - Excel file support
- **transformers** - AI/ML models
- **torch** - Deep learning

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test dashboard
python manage.py test ai_agent
```

## Troubleshooting

### Common Issues

**Problem**: "Python not found"
- **Solution**: Install Python 3.8+ from python.org

**Problem**: "Port already in use"
- **Solution**: Use a different port: python manage.py runserver 8001

**Problem**: "Module not found" errors
- **Solution**: Install requirements: pip install -r requirements.txt

**Problem**: "Permission denied" (Linux/Mac)
- **Solution**: Make scripts executable: chmod +x *.sh

**Problem**: Database errors
- **Solution**: Run migrations: python manage.py migrate

### Getting Help

- Check existing [Issues](https://github.com/Kamranghafar92/Track360/issues)
- Read the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- Create a new issue with detailed information

## Security

Please report security vulnerabilities to the repository maintainers. See [SECURITY.md](SECURITY.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Kamran Ghaffar** - Project Owner and Creator

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- UI components inspired by modern dashboard designs
- Community contributors

## Roadmap

- [ ] Multi-tenant support
- [ ] Advanced reporting and analytics
- [ ] Mobile responsive improvements
- [ ] API endpoints for integration
- [ ] Docker containerization
- [ ] Cloud deployment templates

## Support

If you find this project useful, please consider:
- Giving it a star on GitHub
- Contributing to the codebase
- Reporting bugs and suggesting features
- Sharing it with others

---

**Made with ❤️ by Kamran Ghaffar**
