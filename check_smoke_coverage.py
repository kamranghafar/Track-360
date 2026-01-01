from django.db import connection
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dashboard_project.settings')
django.setup()

with connection.cursor() as cursor:
    # First, let's check what tables exist in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])

    # Now let's check the Project model table structure
    print("\nChecking Project model table structure:")
    cursor.execute("PRAGMA table_info(dashboard_project)")
    columns = cursor.fetchall()
    print("Columns in dashboard_project table:")
    for column in columns:
        print(column)

    # Let's also check if there's a table named dashboard_project
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dashboard_project';")
    dashboard_project_table = cursor.fetchone()
    if dashboard_project_table:
        print("\ndashboard_project table exists")
    else:
        print("\ndashboard_project table does not exist")

    # Let's check if there's a table for the Project model
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%project%';")
    project_tables = cursor.fetchall()
    print("\nTables with 'project' in the name:")
    for table in project_tables:
        print(table[0])

        # Check the structure of each project-related table
        print(f"\nChecking structure of {table[0]}:")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        table_columns = cursor.fetchall()
        for column in table_columns:
            print(column)
