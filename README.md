# Project Dashboard
# Product Dashboard Application

## Overview

This Django-based application provides a comprehensive dashboard for managing products, resources, automation efforts, and team planning. It includes an AI assistant feature that provides context-aware help.

## Installation

1. Clone the repository
2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install django
```

4. Apply migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Troubleshooting

### Chat Window Connection Issues

If you see "127.0.0.1 refused to connect" error in the chat window:

1. Make sure the Django server is running on port 8000
2. Check that you're accessing the application from the same host that the server is running on
3. If using a different host or port, update the `CSRF_TRUSTED_ORIGINS` in settings.py

## Features

- Resource Management
- Product/Project Management
- Automation Updates
- Quarter Planning
- Resource Planning
- KPI Management
- Adhoc Task Management
- AI Assistant

See the USER_MANUAL.md for detailed usage instructions.
A Django-based dashboard application for managing resources and projects. This application allows you to create resources, create projects, assign resources to projects, and view analytics on a dashboard.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Setup Instructions

### 1. Clone the repository

```
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a virtual environment

#### Windows
```
python -m venv .venv
.\.venv\Scripts\activate
```

#### macOS/Linux
```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Apply migrations

```
python manage.py migrate
```

### 5. Create a superuser (admin)

```
python manage.py createsuperuser
```
Follow the prompts to create a username, email, and password.

### 6. Clean the database (optional)

If you want to remove all dummy data from the database:

```
python manage.py clean_database
```

This command will remove all data while preserving the database structure.

### 7. Run the development server

```
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Usage

1. **Dashboard**: The main dashboard shows analytics about projects and resources.
   - Access at: http://127.0.0.1:8000/

2. **Resources**: Manage your resources (people).
   - List: http://127.0.0.1:8000/dashboard/resources/
   - Add: http://127.0.0.1:8000/dashboard/resources/new/

3. **Projects**: Manage your projects.
   - List: http://127.0.0.1:8000/dashboard/projects/
   - Add: http://127.0.0.1:8000/dashboard/projects/new/

4. **Assign Resources**: Assign resources to projects.
   - From the project detail page, click "Assign Resource"

5. **Automation Updates**: Schedule and manage automation updates meetings.
   - List: http://127.0.0.1:8000/dashboard/weekly-meetings/
   - Add: http://127.0.0.1:8000/dashboard/weekly-meetings/new/
   - Start a meeting: From the meeting detail page, click "Start Meeting"
   - Update projects during a meeting: Use the form on the meeting detail page
   - End a meeting: From the meeting detail page, click "End Meeting"

6. **Quarterly Planning**: Manage quarterly targets and planning.
   - List Quarters: http://127.0.0.1:8000/dashboard/quarters/
   - Add Quarter: http://127.0.0.1:8000/dashboard/quarters/new/
   - Add Target: From the quarter detail page, click "Add Target"
   - Assign Resources to Target: From the target detail page, click "Assign Resource"
   - View Timeline: http://127.0.0.1:8000/dashboard/quarters/timeline/
   - View Dashboard: http://127.0.0.1:8000/dashboard/quarters/dashboard/
   - Complete Quarter: From the quarter detail page, click "Mark as Completed"

7. **Admin Interface**: Access the Django admin interface.
   - URL: http://127.0.0.1:8000/admin/
   - Login with the superuser credentials created earlier

## Features

### Core Features
- Create, view, update, and delete resources
- Create, view, update, and delete projects
- Assign resources to projects
- View project and resource analytics on the dashboard
- Track project status, budget, and timeline
- Monitor resource allocation across projects
- Import and export resources and products in CSV or Excel formats
- Download sample import files for resources and products
- AI assistant with Model Context Protocol (MCP) for dashboard context-aware interactions

### Automation Tracking
- Track automation status (smoke and regression)
- Monitor pipeline schedules
- Record test case counts and automation coverage
- Track bugs found through automation
- Document automation framework and tech stack

### Automation Updates
- Schedule and manage automation updates meetings
- Record project updates during meetings
- Generate meeting summaries with changes
- Track historical project updates

### Quarterly Planning
- Define quarterly targets for projects
- Assign resources to quarterly targets
- Track target achievement and completion
- View quarterly timeline and dashboards
- Generate quarterly summary reports
