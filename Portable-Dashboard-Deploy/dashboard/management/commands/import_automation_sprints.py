from django.core.management.base import BaseCommand
from django.utils import timezone
from dashboard.models import Project, Resource, AutomationSprint
import pandas as pd
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Imports automation sprint data from the QA Automation Sprint Alignment Excel file'

    def _parse_dev_resources(self, value):
        """
        Parse the Total Dev Resources field, extracting the first number from strings like "3 (Shared resources)".
        Returns 0 if no number can be extracted.
        """
        if pd.isna(value):
            return 0

        try:
            # Try direct conversion first
            return int(value)
        except (ValueError, TypeError):
            try:
                # Extract the first number from the string
                import re
                dev_resources_str = str(value)
                numbers = re.findall(r'\d+', dev_resources_str)
                if numbers:
                    return int(numbers[0])
                else:
                    self.stdout.write(self.style.WARNING(f'Could not extract number from Total Dev Resources: {dev_resources_str}'))
                    return 0
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error parsing Total Dev Resources: {value}. Error: {e}'))
                return 0

    def handle(self, *args, **options):
        self.stdout.write('Importing automation sprint data from Excel file...')

        # Path to the Excel file
        excel_file = os.path.join(os.getcwd(), "QA Automation Sprint Alignment.xlsx")

        if not os.path.exists(excel_file):
            self.stdout.write(self.style.ERROR(f'Excel file not found: {excel_file}'))
            return

        try:
            # Read the Excel file
            df = pd.read_excel(excel_file)

            # Check if the dataframe is empty
            if df.empty:
                self.stdout.write(self.style.ERROR('Excel file is empty'))
                return

            # Map Excel columns to model fields
            field_mapping = {
                'Product': 'product',
                'EM Name': 'engineering_manager_name',
                'Sprint Length': 'sprint_length',
                'Total Dev Resources': 'total_dev_resources',
                'Decision: 6th Sprint vs. 20%': 'sprint_type',
                'Start Date': 'start_date',
                'Status': 'status',
                'Rationale': 'rationale',
                'Blockers / Risks': 'risks',
                'QA POC': 'qa_point_of_contact',
                'Dev Training Status': 'dev_training_status',
                'Notes / Follow-up': 'notes'
            }

            # Count for statistics
            sprints_created = 0
            sprints_updated = 0
            errors = 0

            # Process each row in the dataframe
            for index, row in df.iterrows():
                try:
                    # Get or create the product
                    product_name = row['Product']
                    try:
                        product = Project.objects.get(name=product_name)
                    except Project.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Product not found: {product_name}. Skipping this row.'))
                        continue

                    # Get or create the QA POC resource
                    qa_poc_name = row['QA POC']
                    qa_poc = None
                    if pd.notna(qa_poc_name):
                        # Handle multiple names separated by slashes
                        primary_qa_name = qa_poc_name.split('/')[0].strip()
                        try:
                            qa_poc = Resource.objects.get(name=primary_qa_name)
                        except Resource.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f'QA POC not found: {primary_qa_name}. This field will be left empty.'))

                    # Convert sprint length to choice format
                    sprint_length = None
                    if pd.notna(row['Sprint Length']):
                        try:
                            sprint_length_value = int(float(row['Sprint Length']))
                            if sprint_length_value == 1:
                                sprint_length = '1_week'
                            elif sprint_length_value == 2:
                                sprint_length = '2_weeks'
                            elif sprint_length_value == 3:
                                sprint_length = '3_weeks'
                        except (ValueError, TypeError):
                            self.stdout.write(self.style.WARNING(f'Invalid sprint length value: {row["Sprint Length"]}. Using default.'))
                            sprint_length = '2_weeks'  # Default value

                    # Convert sprint type to choice format
                    sprint_type = None
                    if pd.notna(row['Decision: 6th Sprint vs. 20%']):
                        sprint_type_value = row['Decision: 6th Sprint vs. 20%']
                        if sprint_type_value == '6th Sprint':
                            sprint_type = '6th_sprint'
                        elif sprint_type_value == 0.2 or sprint_type_value == '20%':
                            sprint_type = '20_allocation'
                        elif sprint_type_value == '7th Sprint':
                            sprint_type = '6th_sprint'  # Map to closest existing choice

                    # Convert status to choice format
                    status = 'to_do'  # Default value
                    if pd.notna(row['Status']):
                        status_value = row['Status']
                        if status_value.lower() == 'in progress':
                            status = 'in_progress'
                        elif status_value.lower() == 'complete':
                            status = 'complete'
                        elif status_value.lower() == 'on hold':
                            status = 'on_hold'

                    # Convert dev training status to choice format
                    dev_training_status = 'to_do'  # Default value
                    if pd.notna(row['Dev Training Status']):
                        training_status = row['Dev Training Status']
                        if training_status.lower() == 'completed':
                            dev_training_status = 'completed'
                        elif training_status.lower() == 'in progress':
                            dev_training_status = 'in_progress'
                        elif training_status.lower() == 'tbd':
                            dev_training_status = 'to_do'

                    # Parse start date
                    start_date = None
                    if pd.notna(row['Start Date']):
                        try:
                            # Try to parse as datetime first
                            if isinstance(row['Start Date'], datetime):
                                start_date = row['Start Date'].date()
                            else:
                                # Try different date formats
                                date_formats = [
                                    '%Y-%m-%d %H:%M:%S',
                                    '%Y-%m-%d',
                                    '%d-%m-%Y',
                                    '%m/%d/%Y',
                                    '%d/%m/%Y',
                                    '%B %d %Y',
                                    '%d %B %Y',
                                    '%b %d %Y',
                                    '%d %b %Y'
                                ]

                                for date_format in date_formats:
                                    try:
                                        start_date = datetime.strptime(str(row['Start Date']), date_format).date()
                                        break
                                    except ValueError:
                                        continue

                                # If none of the formats worked, try a more flexible approach for formats like "15th December 2025"
                                if start_date is None and isinstance(row['Start Date'], str):
                                    date_str = row['Start Date']
                                    # Remove ordinal suffixes
                                    date_str = date_str.replace('st', '').replace('nd', '').replace('rd', '').replace('th', '')
                                    # Try to parse with various formats
                                    for date_format in ['%d %B %Y', '%B %d %Y']:
                                        try:
                                            start_date = datetime.strptime(date_str, date_format).date()
                                            break
                                        except ValueError:
                                            continue
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Error parsing date: {row["Start Date"]}. Error: {e}'))

                    # Check if a sprint already exists for this product and start date
                    existing_sprint = None
                    if start_date:
                        try:
                            existing_sprint = AutomationSprint.objects.get(
                                product=product,
                                start_date=start_date
                            )
                        except AutomationSprint.DoesNotExist:
                            pass

                    # Create or update the sprint
                    if existing_sprint:
                        # Update existing sprint
                        existing_sprint.engineering_manager_name = row['EM Name'] if pd.notna(row['EM Name']) else existing_sprint.engineering_manager_name
                        existing_sprint.sprint_length = sprint_length if sprint_length else existing_sprint.sprint_length
                        # Parse total dev resources
                        existing_sprint.total_dev_resources = self._parse_dev_resources(row['Total Dev Resources'])
                        existing_sprint.sprint_type = sprint_type if sprint_type else existing_sprint.sprint_type
                        existing_sprint.status = status
                        existing_sprint.rationale = row['Rationale'] if pd.notna(row['Rationale']) else existing_sprint.rationale
                        existing_sprint.risks = row['Blockers / Risks'] if pd.notna(row['Blockers / Risks']) else existing_sprint.risks
                        existing_sprint.qa_point_of_contact = qa_poc
                        existing_sprint.dev_training_status = dev_training_status
                        existing_sprint.notes = row['Notes / Follow-up'] if pd.notna(row['Notes / Follow-up']) else existing_sprint.notes

                        existing_sprint.save()
                        sprints_updated += 1
                        self.stdout.write(f'Updated sprint for product: {product.name}, start date: {start_date}')
                    else:
                        # Create new sprint
                        new_sprint = AutomationSprint(
                            product=product,
                            engineering_manager_name=row['EM Name'] if pd.notna(row['EM Name']) else '',
                            sprint_length=sprint_length if sprint_length else '2_weeks',  # Default to 2 weeks
                            total_dev_resources=self._parse_dev_resources(row['Total Dev Resources']),
                            sprint_type=sprint_type if sprint_type else '6th_sprint',  # Default to 6th sprint
                            start_date=start_date if start_date else timezone.now().date(),
                            status=status,
                            rationale=row['Rationale'] if pd.notna(row['Rationale']) else '',
                            risks=row['Blockers / Risks'] if pd.notna(row['Blockers / Risks']) else '',
                            qa_point_of_contact=qa_poc,
                            dev_training_status=dev_training_status,
                            notes=row['Notes / Follow-up'] if pd.notna(row['Notes / Follow-up']) else ''
                        )

                        new_sprint.save()
                        sprints_created += 1
                        self.stdout.write(f'Created new sprint for product: {product.name}, start date: {start_date}')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row {index}: {e}'))
                    errors += 1

            # Print summary
            self.stdout.write(self.style.SUCCESS(f'Import completed: {sprints_created} sprints created, {sprints_updated} sprints updated, {errors} errors'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading Excel file: {e}'))
