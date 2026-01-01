from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Creates tables that are missing in the database'

    def handle(self, *args, **options):
        self.stdout.write('Creating missing tables...')
        
        # SQL statements to create the tables
        sql_statements = [
            """
            CREATE TABLE IF NOT EXISTS "dashboard_sprintcycle" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" varchar(100) NOT NULL UNIQUE,
                "description" text NOT NULL,
                "active" bool NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS "dashboard_oatreleasecycle" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "name" varchar(100) NOT NULL UNIQUE,
                "description" text NOT NULL,
                "active" bool NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS "dashboard_weeklymeeting" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "meeting_date" datetime NOT NULL,
                "title" varchar(200) NOT NULL,
                "notes" text NOT NULL,
                "is_completed" bool NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS "dashboard_weeklyprojectupdate" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "smoke_automation_status" varchar(20) NOT NULL,
                "regression_automation_status" varchar(20) NOT NULL,
                "pipeline_schedule" varchar(20) NOT NULL,
                "execution_time_hours" integer NOT NULL,
                "execution_time_minutes" integer NOT NULL,
                "total_available_test_cases" integer NOT NULL,
                "bugs_found_through_automation" integer NOT NULL,
                "regression_coverage" integer NOT NULL,
                "total_automatable_test_cases" integer NOT NULL,
                "total_automated_test_cases" integer NOT NULL,
                "total_automated_smoke_test_cases" integer NOT NULL,
                "last_automation_run_status" text NOT NULL,
                "last_automation_run_date" date NULL,
                "automation_framework_tech_stack" text NOT NULL,
                "functional_test_cases_count" integer NOT NULL,
                "business_test_cases_count" integer NOT NULL,
                "readiness_for_production" bool NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL,
                "meeting_id" integer NOT NULL REFERENCES "dashboard_weeklymeeting" ("id") DEFERRABLE INITIALLY DEFERRED,
                "oat_release_cycle_id" integer NULL REFERENCES "dashboard_oatreleasecycle" ("id") DEFERRABLE INITIALLY DEFERRED,
                "project_id" integer NOT NULL REFERENCES "dashboard_project" ("id") DEFERRABLE INITIALLY DEFERRED,
                "sprint_cycle_id" integer NULL REFERENCES "dashboard_sprintcycle" ("id") DEFERRABLE INITIALLY DEFERRED,
                "team_lead_id" integer NULL REFERENCES "dashboard_resource" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            """,
            """
            CREATE UNIQUE INDEX IF NOT EXISTS "dashboard_weeklyprojectupdate_meeting_id_project_id_uniq" ON "dashboard_weeklyprojectupdate" ("meeting_id", "project_id");
            """
        ]
        
        with connection.cursor() as cursor:
            for sql in sql_statements:
                cursor.execute(sql)
            
            self.stdout.write(self.style.SUCCESS('Tables created successfully'))
            
            # Check if the tables were created
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            self.stdout.write('Tables in the database:')
            for table in tables:
                self.stdout.write(f'- {table[0]}')
            
            # Check specific tables
            tables_to_check = [
                'dashboard_sprintcycle',
                'dashboard_oatreleasecycle',
                'dashboard_weeklymeeting',
                'dashboard_weeklyprojectupdate'
            ]
            
            for table in tables_to_check:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS(f'Table {table} exists'))
                else:
                    self.stdout.write(self.style.ERROR(f'Table {table} does not exist'))