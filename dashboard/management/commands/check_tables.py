from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Checks if tables exist in the database'

    def handle(self, *args, **options):
        self.stdout.write('Checking tables...')

        with connection.cursor() as cursor:
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
                'dashboard_weeklyprojectupdate',
                'dashboard_project',
                'dashboard_resource',
                'dashboard_projectresource',
                'dashboard_weeklyproductmeeting',
                'dashboard_weeklyproductupdate'
            ]

            for table in tables_to_check:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS(f'Table {table} exists'))
                else:
                    self.stdout.write(self.style.ERROR(f'Table {table} does not exist'))
