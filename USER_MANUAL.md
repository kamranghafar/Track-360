# Track360 - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Getting Started](#getting-started)
4. [Dashboard](#dashboard)
5. [Resource Management](#resource-management)
6. [Product Management](#product-management)
7. [Automation Updates](#automation-updates)
8. [Manual Updates](#manual-updates)
9. [Automation Sprint Management](#automation-sprint-management)
10. [Quarter Targets](#quarter-targets)
11. [Resource Planning](#resource-planning)
12. [KPI Management](#kpi-management)
13. [Adhoc Task Management](#adhoc-task-management)
14. [Production Bug Tracking](#production-bug-tracking)
15. [Documentation Management](#documentation-management)
16. [SOP Management](#sop-management)
17. [Feedback Management](#feedback-management)
18. [Admin Interface](#admin-interface)
19. [Troubleshooting](#troubleshooting)
20. [FAQ](#faq)

## Introduction

Track360 is a comprehensive Django-based QA and Resource Management Dashboard designed to help testing teams manage resources, projects, automation efforts, and quarterly planning. The application provides a centralized platform for tracking project status, resource allocation, automation metrics, and task management.

### Key Features

- **Resource Management**: Track team members, their skills, availability, and assignments with hierarchical relationships
- **Product/Project Management**: Manage products and projects with detailed tracking of automation status and metrics
- **Data Import/Export**: Import and export resources and products in CSV or Excel formats
- **Automation Updates**: Schedule and document automation update meetings with comprehensive metrics tracking
- **Manual Updates**: Schedule and manage manual testing update meetings with problem tracking
- **Automation Sprint Management**: Coordinate dedicated automation sprints with development teams
- **Quarter Planning**: Set quarterly targets, track progress, and assign resources
- **Resource Planning**: Plan resource allocation, track leaves, and monitor utilization
- **KPI Management**: Define, track, and rate Key Performance Indicators for resources on a monthly basis
- **Adhoc Task Management**: Track important tasks (rocks) with priorities and deadlines
- **Production Bug Tracking**: Monitor production issues with severity levels and status workflows
- **Documentation Management**: Maintain product-specific documentation and department-wide documents
- **SOP Management**: Track Standard Operating Procedures with multi-stage status workflows
- **Feedback Management**: Conduct 1:1 feedback sessions and monthly feedback submissions
- **AI Assistant**: Get context-aware help and insights with integrated LLM support

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**

```bash
git clone <repository-url>
cd <repository-directory>
```

2. **Create a virtual environment**

Windows:
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**

```bash
pip install django
```

4. **Apply migrations**

```bash
python manage.py migrate
```

5. **Create a superuser (admin)**

```bash
python manage.py createsuperuser
```
Follow the prompts to create a username, email, and password.

6. **Load sample data (optional)**

```bash
python manage.py add_dummy_data
python manage.py add_rock_dummy_data
python manage.py add_roadmap_dummy_data
```

7. **Clean the database (optional)**

If you want to remove all dummy data from the database:

```bash
python manage.py clean_database
```

This command will remove all data while preserving the database structure. You can verify that the database is empty by running:

```bash
python manage.py verify_clean_database
```

8. **Run the development server**

```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Getting Started

After installation, you can access the application through your web browser. The main interface consists of a sidebar navigation menu and a content area.

### Navigation

The sidebar provides access to all main features of the application:

- **Dashboard**: Overview of projects, resources, and key metrics
- **Resources**: Manage team members
- **Products**: Manage products and their automation status
- **Automation Updates**: Schedule and manage automation update meetings
- **Manual Updates**: Schedule and manage manual update meetings
- **Quarter Targets**: Set and track quarterly targets
- **Resource Planning**: Plan resource allocation and track leaves
- **KPI Management**: Define, track, and rate Key Performance Indicators
- **Adhoc Task Management**: Manage important tasks (rocks)
- **AI Assistant**: Get help and insights with context-aware AI

## Dashboard

The dashboard provides an overview of your projects, resources, and key metrics. It displays:

- Project status summary
- Resource allocation
- Automation status across projects
- Recent automation and manual update meetings
- Upcoming due rocks (tasks)

### Using the Dashboard

- View project status distribution
- Monitor resource utilization
- Track automation progress
- See upcoming meetings and deadlines

## Resource Management

The Resource Management module allows you to manage your team members, their skills, and availability.

### Key Features

- Create, view, update, and delete resources
- Track resource skills and roles
- Monitor resource availability
- View resource assignments across projects and quarters
- Import and export resources in CSV or Excel formats
- Download sample import files

### Managing Resources

#### Adding a New Resource

1. Navigate to Resources in the sidebar
2. Click "Add Resource" button
3. Fill in the required information:
   - Name
   - Email (optional)
   - Role (optional)
   - Lead (optional)
   - Manager (optional)
   - Skill (Automation, Manual, or Both)
   - Availability
4. Click "Create Resource"

#### Viewing Resource Details

1. Navigate to Resources in the sidebar
2. Click on a resource name in the list
3. View detailed information about the resource, including:
   - Personal information
   - Assigned projects
   - Quarterly targets
   - Rocks (tasks)

#### Editing a Resource

1. Navigate to the resource detail page
2. Click "Edit" button
3. Update the information as needed
4. Click "Update Resource"

#### Deleting a Resource

1. Navigate to the resource detail page
2. Click "Delete" button
3. Confirm deletion

#### Importing Resources

1. Navigate to Resources in the sidebar
2. Click "Import" button
3. Download a sample file (CSV or Excel) to understand the required format
4. Prepare your import file with the following columns:
   - name (required): The name of the resource
   - email: The email address of the resource
   - role: The role of the resource
   - skill: The skill of the resource (automation, manual, or both)
   - availability: The availability of the resource (true/false, yes/no, 1/0)
5. Click "Choose File" and select your prepared file
6. Click "Import Resources"
7. Review the success message or error details

#### Exporting Resources

1. Navigate to Resources in the sidebar
2. Click "Export" dropdown button
3. Select the desired format (CSV or Excel)
4. The file will be downloaded to your computer

## Product Management

The Product Management module allows you to manage your products and their automation status.

### Key Features

- Create, view, update, and delete products
- Track product status and timeline
- Monitor automation metrics
- Assign resources to products
- View historical updates from automation and manual update meetings
- Import and export products in CSV or Excel formats
- Download sample import files

### Managing Products

#### Adding a New Product

1. Navigate to Products in the sidebar
2. Click "Add Product" button
3. Fill in the required information:
   - Name
   - Description (optional)
   - Start Date
   - End Date (optional)
   - Status
4. Fill in automation details (optional):
   - Smoke Automation Status
   - Regression Automation Status
   - Pipeline Schedule
   - Execution Time of Smoke
   - Test Case Counts
   - Automation Framework
   - Team Lead
   - And more
5. Click "Create Product"

#### Viewing Product Details

1. Navigate to Products in the sidebar
2. Click on a product name in the list
3. View detailed information about the product, including:
   - Basic information
   - Automation details
   - Assigned resources
   - Historical updates from automation and manual update meetings

#### Assigning Resources to a Product

1. Navigate to the product detail page
2. Click "Assign Resource" button
3. Select a resource from the dropdown
4. Enter hours allocated and utilization percentage
5. Add notes (optional)
6. Click "Assign Resource"

#### Editing a Product

1. Navigate to the product detail page
2. Click "Edit" button
3. Update the information as needed
4. Click "Update Product"

#### Deleting a Product

1. Navigate to the product detail page
2. Click "Delete" button
3. Confirm deletion

#### Importing Products

1. Navigate to Products in the sidebar
2. Click "Import" button
3. Download a sample file (CSV or Excel) to understand the required format
4. Prepare your import file with the following columns:
   - name (required): The name of the product
   - description: The description of the product
   - start_date: The start date of the product (YYYY-MM-DD format)
   - end_date: The end date of the product (YYYY-MM-DD format, can be empty)
   - status: The status of the product (not_started, in_progress, completed, on_hold)
5. Click "Choose File" and select your prepared file
6. Click "Import Products"
7. Review the success message or error details

#### Exporting Products

1. Navigate to Products in the sidebar
2. Click "Export" dropdown button
3. Select the desired format (CSV or Excel)
4. The file will be downloaded to your computer

## Automation Updates

The Automation Updates module allows you to schedule and document meetings to track automation progress.

### Key Features

- Schedule automation update meetings
- Record project updates during meetings
- Track automation metrics over time
- Generate meeting summaries

### Managing Automation Updates

#### Scheduling a New Meeting

1. Navigate to Automation Updates in the sidebar
2. Click "Schedule Meeting" button
3. Enter meeting details:
   - Title
   - Date and Time
   - Notes (optional)
4. Click "Schedule Meeting"

#### Starting a Meeting

1. Navigate to the meeting detail page
2. Click "Start Meeting" button
3. The meeting status will change to "In Progress"
4. Projects will be loaded for updates

#### Updating Projects During a Meeting

1. During an active meeting, click "Update" next to a project
2. Fill in the updated automation metrics:
   - Smoke Automation Status
   - Regression Automation Status
   - Pipeline Schedule
   - Test Case Counts
   - And more
3. Click "Save Updates"

#### Ending a Meeting

1. When all updates are complete, click "End Meeting" button
2. The meeting status will change to "Completed"
3. A summary of changes will be generated

#### Viewing Meeting History

1. Navigate to Automation Updates in the sidebar
2. View the list of past meetings
3. Click on a meeting to see details and updates

## Manual Updates

Similar to Automation Updates, but focused on product-specific updates rather than automation metrics.

### Key Features

- Schedule manual update meetings
- Record product updates and issues
- Track problem resolution
- Document product status

### Managing Manual Updates

The workflow is similar to Automation Updates, but with different update fields focused on product status, problems, and solutions.

## Automation Sprint Management

The Automation Sprint Management module enables QA teams to coordinate and track dedicated automation sprints where development teams work on test automation alongside or as part of their regular sprint cycles.

### Key Features

- Track dedicated automation sprints with development teams
- Support for "6th Sprint" (dedicated sprint) and "20% Allocation" (time percentage) models
- Monitor developer training status and readiness
- Track sprint metrics including planned vs. automated test cases
- Document sprint rationale, risks, and follow-up notes
- Assign QA points of contact for each sprint
- Import sprint data from Excel files
- Filter and view sprints by product, status, and sprint type

### Understanding Automation Sprint Models

**6th Sprint Model**: In this model, every 6th sprint is dedicated entirely to automation work. Development teams pause feature development to focus on test automation, allowing for concentrated automation efforts.

**20% Allocation Model**: In this model, developers allocate 20% of their time in each sprint to automation work, allowing for continuous automation progress alongside feature development.

### Managing Automation Sprints

#### Creating a New Automation Sprint

1. Navigate to Automation Sprint Management in the sidebar
2. Click "Add Sprint" button
3. Fill in sprint setup details:
   - **Product**: Select the product/project for this sprint
   - **Engineering Manager Name**: Name of the engineering manager overseeing the sprint
   - **Sprint Length**: Choose 1, 2, or 3 weeks
   - **Total Dev Resources**: Number of developers allocated to automation
   - **Sprint Type**: Select "6th Sprint" or "20% Allocation"
   - **Start Date**: When the sprint begins
   - **QA POC**: Select the QA point of contact for coordination
4. Fill in planning details:
   - **Status**: To Do, In Progress, Complete, or On Hold
   - **Rationale**: Why this sprint is being conducted
   - **Risks**: Potential blockers or risks
   - **Dev Training Status**: Completed, In Progress, or To Do
   - **Notes/Follow-up**: Additional notes or action items
5. Click "Create Sprint"

#### Viewing Sprint Details

1. Navigate to Automation Sprint Management in the sidebar
2. Click on a sprint in the list
3. View comprehensive sprint information including:
   - Sprint setup and configuration
   - Current status and training status
   - Metrics (if recorded)
   - Rationale and risk documentation
   - Notes and follow-up items

#### Updating Sprint Metrics

Once a sprint is underway or completed, you can record actual metrics:

1. Navigate to the sprint detail page
2. Click "Update Metrics" button
3. Enter the actual metrics:
   - **Total Sprint Days**: Actual number of days the sprint ran
   - **Total Planned Working Hours**: Hours allocated for automation work
   - **Blocked Hours**: Hours lost to blockers or impediments
   - **Total Planned Test Cases**: Number of test cases targeted for automation
   - **Total Test Cases Automated**: Number of test cases actually automated
4. Click "Save Metrics"

The system will automatically calculate:
- **Net Working Hours**: Planned hours minus blocked hours
- **Automation Completion Rate**: Percentage of planned test cases that were automated

#### Editing a Sprint

1. Navigate to the sprint detail page
2. Click "Edit Sprint" button
3. Update any sprint information as needed
4. Click "Update Sprint"

#### Deleting a Sprint

1. Navigate to the sprint detail page
2. Click "Delete Sprint" button
3. Confirm deletion

#### Filtering Sprints

On the sprint list page, you can filter sprints by:
- **Product**: View sprints for a specific product
- **Status**: Filter by To Do, In Progress, Complete, or On Hold
- **Sprint Type**: Show only 6th Sprint or 20% Allocation sprints

#### Importing Sprints from Excel

If you have sprint data in an Excel file, you can import it in bulk:

1. Prepare an Excel file with the following columns:
   - Product (product name)
   - EM Name (engineering manager name)
   - Sprint Length (1, 2, or 3)
   - Total Dev Resources (number)
   - Decision: 6th Sprint vs. 20% ("6th Sprint" or "20% Allocation")
   - Start Date (YYYY-MM-DD format)
   - Status (To Do/In Progress/Complete/On Hold)
   - Rationale (text)
   - Blockers/Risks (text)
   - QA POC (resource name)
   - Dev Training Status (Completed/In Progress/To Do)
   - Notes/Follow-up (text)

2. Use the management command to import:
```bash
python manage.py import_automation_sprints
```

The system will match product names and QA POC names to existing records and create the sprint entries.

### Best Practices

1. **Plan Ahead**: Create sprint entries in advance with "To Do" status to facilitate planning discussions
2. **Document Rationale**: Always document why a sprint is being conducted to maintain historical context
3. **Track Risks Early**: Document potential risks upfront to enable proactive mitigation
4. **Update Status Regularly**: Keep sprint status current to provide accurate visibility
5. **Record Metrics Promptly**: Update metrics as soon as the sprint completes while data is fresh
6. **Review Training Needs**: Ensure developer training is completed before sprint starts
7. **Coordinate with QA POC**: Ensure the QA point of contact is actively engaged throughout the sprint

### Sprint Status Workflow

**To Do**: Sprint is planned but not yet started. Use this status during planning phases.

**In Progress**: Sprint is actively running. Development team is working on automation.

**Complete**: Sprint has finished and metrics have been recorded.

**On Hold**: Sprint has been paused or delayed. Document the reason in notes.

### Developer Training Status

**To Do**: Developers need training on automation frameworks and tools before the sprint.

**In Progress**: Training is currently being conducted or in progress.

**Completed**: All developers have completed necessary training and are ready for automation work.

## Quarter Targets

The Quarter Targets module allows you to set and track quarterly goals for your projects.

### Key Features

- Define quarters with start and end dates
- Set targets for projects in each quarter
- Assign resources to targets
- Track target achievement
- Generate quarterly reports

### Managing Quarters and Targets

#### Creating a New Quarter

1. Navigate to Quarter Targets in the sidebar
2. Click "Add Quarter" button
3. Enter quarter details:
   - Year
   - Quarter Number
   - Name (optional)
4. Click "Create Quarter"

#### Adding a Target to a Quarter

1. Navigate to the quarter detail page
2. Click "Add Target" button
3. Select a project
4. Enter target description and value
5. Click "Create Target"

#### Assigning Resources to a Target

1. Navigate to the target detail page
2. Click "Assign Resource" button
3. Select a resource
4. Enter allocation percentage
5. Add notes (optional)
6. Click "Assign Resource"

#### Completing a Quarter

1. Navigate to the quarter detail page
2. Click "Mark as Completed" button
3. Enter completion notes
4. Update achievement values for each target
5. Click "Complete Quarter"

#### Viewing Quarter Dashboard

1. Navigate to Quarter Targets in the sidebar
2. Click "Dashboard" button
3. View summary statistics and charts for all quarters

#### Viewing Quarter Timeline

1. Navigate to Quarter Targets in the sidebar
2. Click "Timeline" button
3. View a visual timeline of all quarters and their targets

## Resource Planning

The Resource Planning module allows you to plan resource allocation across projects and track leaves.

### Key Features

- View resource allocation across projects
- Assign resources to projects with specific dates
- Manage resource leaves
- Identify resource conflicts and overallocation

### Managing Resource Planning

#### Viewing Resource Allocation

1. Navigate to Resource Planning in the sidebar
2. View the resource allocation chart showing assignments across projects

#### Assigning Resources with Dates

1. Navigate to Resource Planning in the sidebar
2. Click "Assign Resource" next to a project
3. Select a resource
4. Enter start date, end date, hours allocated, and utilization percentage
5. Click "Assign Resource"

#### Managing Resource Leaves

1. Navigate to Resource Planning in the sidebar
2. Click "Add Leave" button
3. Select a resource
4. Enter leave details:
   - Start Date
   - End Date
   - Leave Type
   - Description (optional)
5. Click "Create Leave"

## KPI Management

The KPI Management module allows you to define, track, and rate Key Performance Indicators (KPIs) for resources on a monthly basis.

### Key Features

- Create and manage KPIs for each resource
- Rate KPIs on a scale of 1-5 for each month
- Add optional remarks for each KPI rating
- Provide mandatory overall remarks when submitting ratings
- View historical ratings for each KPI
- Track all rating submissions by month/year

### Managing KPIs

#### Accessing KPI Management

1. Navigate to KPI Management in the sidebar
2. View the list of resources with their KPI counts
3. Use the search box to find specific resources

#### Adding a New KPI

1. Navigate to KPI Management in the sidebar
2. Click on a resource name to view their KPIs
3. Click "Add KPI" button
4. Enter KPI details:
   - Name
   - Description (optional)
5. Click "Save KPI"

#### Rating KPIs

1. Navigate to KPI Management in the sidebar
2. Click on a resource name to view their KPIs
3. Click "Rate KPIs (Current Month)" button
4. For each KPI:
   - Select a rating from 1 to 5
   - Add optional remarks
5. Enter mandatory overall remarks
6. Click "Submit Ratings"

#### Viewing KPI Details

1. Navigate to KPI Management in the sidebar
2. Click on a resource name to view their KPIs
3. Click "View" next to a KPI
4. View detailed information about the KPI, including:
   - KPI name and description
   - Average rating
   - Rating history

#### Viewing Submission History

1. Navigate to KPI Management in the sidebar
2. Click on a resource name to view their KPIs
3. Click "View Submission History" button
4. View a list of all KPI rating submissions for the resource
5. Click "View Details" to see the full submission

### Rating Scale

The KPI rating scale is defined as follows:

1. **Poor**: Performance is significantly below expectations
2. **Below Expectations**: Performance is somewhat below expectations
3. **Meets Expectations**: Performance meets expectations
4. **Exceeds Expectations**: Performance exceeds expectations
5. **Outstanding**: Performance is exceptional and far exceeds expectations

## Rock Management

The Rock Management module allows you to track important tasks (rocks) with priorities and deadlines.

### Key Features

- Create, view, update, and delete rocks (tasks)
- Assign rocks to resources
- Set priorities and deadlines
- Track rock status
- View rocks by status, priority, assignee, and project

### Managing Rocks

#### Adding a New Rock

1. Navigate to Rock Management in the sidebar
2. Click "Add Rock" button
3. Enter rock details:
   - Title
   - Description (optional)
   - Priority
   - Assignee
   - Project (optional)
   - Quarter Target (optional)
   - Due Date (optional)
4. Click "Create Rock"

#### Viewing Rock Details

1. Navigate to Rock Management in the sidebar
2. Click on a rock title in the list
3. View detailed information about the rock

#### Starting a Rock

1. Navigate to the rock detail page
2. Click "Start Rock" button
3. The rock status will change to "In Progress"

#### Completing a Rock

1. Navigate to the rock detail page
2. Click "Complete Rock" button
3. The rock status will change to "Completed"

#### Viewing Rock Dashboard

1. Navigate to Rock Management in the sidebar
2. Click "Dashboard" button
3. View summary statistics and charts for all rocks

## Strategic Roadmap

The Strategic Roadmap module allows you to visualize and manage strategic goals, milestones, and deliverables in a timeline view.

### Key Features

- View all targets for the current quarter in a roadmap-style layout
- Understand the status, progress, and ownership of each roadmap item
- Add new roadmap items directly to the timeline
- Filter and sort roadmap items by owner, project, or status
- Track item progress from "Not Started" to "Completed"

### Managing Roadmap Items

#### Viewing the Roadmap Timeline

1. Navigate to Strategic Roadmap in the sidebar
2. View the timeline display of all roadmap items for the current quarter
3. Use the dropdown to switch between quarters
4. Filter items by owner, project, or status

#### Adding a New Roadmap Item

1. Navigate to Strategic Roadmap in the sidebar
2. Click "Add Roadmap Item" button
3. Enter roadmap item details:
   - Title
   - Description (optional)
   - Owner
   - Start and End Dates
   - Status
   - Quarter
   - Project (optional)
   - Quarter Target (optional)
4. Click "Create"

#### Viewing Roadmap Item Details

1. Navigate to Strategic Roadmap in the sidebar
2. Click on a roadmap item in the timeline or list view
3. View detailed information about the roadmap item

#### Updating a Roadmap Item's Status

1. Navigate to the roadmap item detail page
2. Click "Start Item" to change status to "In Progress"
3. Click "Complete Item" to change status to "Completed"

#### Viewing All Roadmap Items

1. Navigate to Strategic Roadmap in the sidebar
2. Click "View All Items" button
3. View a table of all roadmap items
4. Filter and sort items as needed

## Production Bug Tracking

The Production Bug Tracking module allows you to monitor and manage bugs found in production environments.

### Key Features

- Track production bugs with severity levels
- Multi-stage status workflow from open to done
- Link bugs to products and test cases
- Connect to external bug tracking systems (GOPS, Product Boards)
- View bug history and status changes

### Managing Production Bugs

#### Adding a New Production Bug

1. Navigate to Production Bug Tracking in the sidebar
2. Click "Add Bug" button
3. Fill in bug details:
   - **Title**: Brief description of the bug
   - **Description**: Detailed description of the issue
   - **Product**: Link to the affected product
   - **Severity**: High, Medium, or Low
   - **Status**: Open (default)
   - **GOPS Link**: Link to GOPS ticket (optional)
   - **Product Board Link**: Link to product board item (optional)
   - **Test Case Added**: Yes/No - whether a test case has been added to prevent regression
4. Click "Create Bug"

#### Viewing Bug Details

1. Navigate to Production Bug Tracking in the sidebar
2. Click on a bug in the list
3. View comprehensive bug information including:
   - Bug details and description
   - Current status and severity
   - Associated product
   - External links
   - Test case status
   - Status history

#### Updating Bug Status

Production bugs follow a workflow through multiple states:

1. **Open**: Bug has been reported and logged
2. **In Progress**: Bug is being investigated or fixed
3. **Resolved**: Fix has been implemented
4. **Tested**: Fix has been verified in test environment
5. **Done**: Fix has been deployed to production and verified

To update bug status:
1. Navigate to the bug detail page
2. Click "Update Status" button
3. Select the new status
4. Add notes about the status change (optional)
5. Click "Save"

#### Filtering Bugs

On the bug list page, filter bugs by:
- **Product**: View bugs for specific products
- **Severity**: Filter by High, Medium, or Low severity
- **Status**: Show bugs in specific status stages
- **Test Case Added**: Filter by whether test cases have been added

#### Severity Levels

**High**: Critical bugs affecting core functionality or large user base. Requires immediate attention.

**Medium**: Bugs affecting functionality but with workarounds available. Should be addressed in next release.

**Low**: Minor issues with minimal impact. Can be addressed in future releases.

## Documentation Management

The Documentation Management module helps you organize and maintain links to various types of documentation.

### Key Features

- Maintain product-specific documentation links
- Manage department-wide document repositories
- Track automation runner boards
- Quick access to Confluence and external documentation

### Managing Product Documentation

#### Adding Product Documentation

1. Navigate to a product detail page
2. Scroll to the Documentation section
3. Click "Add Documentation" button
4. Enter documentation details:
   - **Title**: Name of the document
   - **URL**: Link to the documentation
   - **Description**: Brief description (optional)
5. Click "Save"

#### Viewing Product Documentation

1. Navigate to Documentation in the sidebar, or
2. View from a product detail page
3. Click on documentation links to access external documents

### Managing Department Documents

Department documents are organization-wide documentation accessible to all users.

#### Adding Department Documents

1. Navigate to Department Documents in the sidebar
2. Click "Add Document" button
3. Enter document details:
   - **Title**: Document name
   - **URL**: Confluence or external link
   - **Category**: Type of document (optional)
4. Click "Save"

#### Viewing Department Documents

1. Navigate to Department Documents in the sidebar
2. Browse or search for documents
3. Click on links to access documents

### Managing Automation Runners

Automation Runner boards track where automation tests are executed.

#### Adding Automation Runner

1. Navigate to Automation Runners in the sidebar
2. Click "Add Runner" button
3. Enter runner details:
   - **Name**: Runner identifier
   - **URL**: Link to runner board or dashboard
   - **Description**: Details about the runner
4. Click "Save"

## SOP Management

The SOP (Standard Operating Procedure) Management module helps you track and manage organizational procedures through their lifecycle.

### Key Features

- Multi-stage status workflow for SOP lifecycle
- Automatic status history tracking
- Version control through status changes
- Track SOPs from creation to rollout

### Understanding SOP Status Workflow

SOPs progress through multiple stages:

1. **In Progress**: SOP is being drafted
2. **Under Review**: SOP is ready for review by stakeholders
3. **Review Done**: Review is complete, changes incorporated
4. **Rollout in Progress**: SOP is being communicated and implemented
5. **Rollout Done**: SOP implementation is complete
6. **Active**: SOP is live and in use
7. **Inactive**: SOP has been deprecated or replaced

### Managing SOPs

#### Creating a New SOP

1. Navigate to SOP Management in the sidebar
2. Click "Add SOP" button
3. Enter SOP details:
   - **Title**: Name of the procedure
   - **Description**: Detailed description of the SOP
   - **Document Link**: Link to full SOP document (Confluence, etc.)
   - **Owner**: Person responsible for the SOP
   - **Status**: In Progress (default)
   - **Version**: Version number (optional)
4. Click "Create SOP"

#### Viewing SOP Details

1. Navigate to SOP Management in the sidebar
2. Click on an SOP in the list
3. View comprehensive information including:
   - SOP details and description
   - Current status
   - Owner information
   - Document link
   - Status history with timestamps

#### Updating SOP Status

The system automatically tracks status changes:

1. Navigate to the SOP detail page
2. Click "Update Status" button
3. Select the new status from the workflow
4. Add notes about the update (optional)
5. Click "Save"

The system will automatically record:
- Previous status
- New status
- Date and time of change
- User who made the change

#### Filtering SOPs

On the SOP list page, filter by:
- **Status**: View SOPs in specific workflow stages
- **Owner**: See SOPs owned by specific individuals
- **Active/Inactive**: Filter active vs. inactive SOPs

#### Viewing Status History

1. Navigate to the SOP detail page
2. Scroll to the Status History section
3. View complete history of all status changes with:
   - Previous and new status
   - Date and time of change
   - User who made the change

### Best Practices

1. **Keep SOPs Current**: Regularly review and update SOPs to reflect current processes
2. **Document Changes**: Add notes when changing status to maintain context
3. **Version Control**: Update version numbers when making significant changes
4. **Regular Reviews**: Schedule periodic reviews of active SOPs
5. **Archive Properly**: Mark outdated SOPs as inactive rather than deleting them

## Feedback Management

The Feedback Management module enables structured feedback processes for team members.

### Key Features

- Conduct 1:1 feedback sessions
- Submit monthly feedback forms
- Track feedback history
- Monitor feedback submission status

### One-on-One Feedback

One-on-one feedback sessions allow managers and leads to document feedback discussions with team members.

#### Recording a 1:1 Feedback Session

1. Navigate to Feedback Management in the sidebar
2. Select "1:1 Feedbacks" option
3. Click "Add Feedback" button
4. Select the resource (team member)
5. Enter feedback details:
   - **Date**: Date of the feedback session
   - **Feedback Notes**: Discussion points and feedback provided
   - **Action Items**: Follow-up tasks or improvements (optional)
   - **Next Review Date**: When to follow up (optional)
6. Click "Save Feedback"

#### Viewing 1:1 Feedback History

1. Navigate to Feedback Management in the sidebar
2. Select "1:1 Feedbacks" option
3. Filter by resource or date range
4. Click on a feedback entry to view full details

### Monthly Feedback

Monthly feedback provides a structured process for submitting periodic feedback forms.

#### Submitting Monthly Feedback

1. Navigate to Feedback Management in the sidebar
2. Select "Monthly Feedback" option
3. View list of pending feedback submissions
4. Click "Submit Feedback" for a specific resource and month
5. Fill in the feedback form:
   - **Performance Summary**: Overall performance assessment
   - **Strengths**: Areas where the resource excels
   - **Areas for Improvement**: Development opportunities
   - **Goals for Next Month**: Objectives and targets
   - **Additional Comments**: Any other relevant feedback
6. Click "Submit"

The feedback status will change from "Due" to "Submitted"

#### Viewing Monthly Feedback History

1. Navigate to Feedback Management in the sidebar
2. Select "Monthly Feedback" option
3. Use filters to find specific submissions:
   - **Resource**: View feedback for specific team member
   - **Month/Year**: Filter by time period
   - **Status**: Show due or submitted feedback
4. Click on an entry to view full feedback details

#### Managing Feedback Status

**Due**: Feedback is pending submission for the month

**Submitted**: Feedback has been completed and submitted

### Best Practices

1. **Timely Submission**: Submit monthly feedback before the deadline
2. **Be Specific**: Provide concrete examples in feedback
3. **Balance Feedback**: Include both strengths and areas for improvement
4. **Set Clear Goals**: Define actionable goals for the next period
5. **Follow Up**: Reference previous feedback in 1:1 sessions to track progress
6. **Document Regularly**: Don't wait until formal review periods to document feedback

## Admin Interface

The Django Admin Interface provides advanced management capabilities for administrators.

### Accessing the Admin Interface

1. Navigate to http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials

### Admin Features

- Manage all application models
- Perform bulk operations
- Configure system settings
- Manage user accounts and permissions

## Troubleshooting

### Common Issues and Solutions

#### Application Not Starting

**Issue**: The application fails to start with an error message.

**Solution**:
1. Ensure Python and Django are properly installed
2. Check that all migrations have been applied
3. Verify the database file exists and is not corrupted
4. Check for syntax errors in custom code

#### Database Migration Errors

**Issue**: Errors when running migrations.

**Solution**:
1. Backup your database
2. Try running `python manage.py makemigrations` first
3. If issues persist, consider resetting migrations (advanced)

#### Resource Assignment Conflicts

**Issue**: Unable to assign a resource due to conflicts.

**Solution**:
1. Check the resource's current assignments
2. Verify the resource's availability status
3. Check for overlapping leave periods
4. Adjust allocation percentages if necessary

## FAQ

### General Questions

**Q: Can I use this application for non-software projects?**

A: Yes, while the application has features specific to software automation, it can be used for any type of project management.

**Q: How do I backup my data?**

A: You can backup the SQLite database file (db.sqlite3) by making a copy of it. For production environments, consider using a more robust database solution with regular backup procedures.

**Q: Can multiple users access the application simultaneously?**

A: Yes, the application supports multiple concurrent users. User management is handled through Django's authentication system.

### Feature-Specific Questions

**Q: What's the difference between Products and Projects?**

A: In this application, they are used interchangeably. The model is called "Project" but some views refer to them as "Products," particularly when focusing on automation aspects.

**Q: How do I calculate resource utilization?**

A: Resource utilization is tracked through the "utilization_percentage" field when assigning resources to projects. The Resource Planning view helps visualize overall utilization across projects.

**Q: What are "Rocks"?**

A: Rocks are important tasks or goals that need to be accomplished. The term comes from the Entrepreneurial Operating System (EOS) methodology, where rocks represent priorities that should be focused on.

**Q: How do I track automation progress over time?**

A: Automation Updates are designed to track automation metrics over time. Each meeting records the current state of automation for each project, allowing you to see trends and progress.

**Q: How does the KPI rating system work?**

A: The KPI Management module allows you to rate resources on predefined Key Performance Indicators (KPIs) on a monthly basis. Each KPI is rated on a scale of 1-5, with optional remarks. When submitting ratings, you must provide overall remarks for the submission. You can view historical ratings and track performance over time.

**Q: What file formats are supported for import and export?**

A: The application supports both CSV and Excel (XLSX) formats for importing and exporting resources and products.

**Q: Can I import multiple resources or products at once?**

A: Yes, you can import multiple resources or products in a single file. The system will process each row in the import file.

**Q: What happens if I import a resource or product that already exists?**

A: If a resource or product with the same name already exists, it will be updated with the new information from the import file. This allows you to use the import feature for both creating new entries and updating existing ones.

## AI Assistant

The AI Assistant feature provides context-aware help and insights about your dashboard data, making it easier to get information and perform actions without having to navigate through multiple screens.

### Enhanced with Open-Source LLM

The AI Assistant has been enhanced with an open-source Large Language Model (LLM) to provide more intelligent and context-aware responses. This integration allows the AI Assistant to:

- Understand a wider variety of questions and phrasings
- Provide more detailed and helpful responses
- Better understand the context of your dashboard
- Handle complex queries that combine multiple types of information

The LLM enhancement works seamlessly with the Model Context Protocol (MCP), using the context information to generate more relevant and accurate responses. For technical details about the LLM integration, see the LLM_INTEGRATION.md file.

### What is Model Context Protocol (MCP)?

Model Context Protocol (MCP) is a framework that allows the AI Assistant to understand the context of your dashboard in real-time. Unlike traditional chatbots that only respond to your direct questions, an MCP-enabled AI Assistant can:

- Understand what you're currently viewing in the dashboard
- See the data and visualizations that are visible to you
- Know what filters you've applied
- Remember your recent actions
- Access relevant information from your projects, resources, and KPIs

This contextual awareness makes the AI Assistant much more helpful and intuitive to use, as it can provide responses that are directly relevant to what you're working on.

### Accessing the AI Assistant

There are two ways to access the AI Assistant:

1. **Chat Bubble**: The AI Assistant is available as a chat bubble in the bottom-right corner of every page in the dashboard. Click on the robot icon to open the chat interface.

2. **Full Page View**: For a larger interface, you can click on the "AI Assistant" option in the sidebar navigation. This will open the full-page chat interface.

### Starting a Conversation

When you first open the AI Assistant, it will greet you with a welcome message. You can then type your question or request in the input field at the bottom of the chat interface and press Enter or click the Send button.

The AI Assistant will automatically collect context from your current dashboard view before responding, ensuring that its answers are relevant to what you're currently working on.

### How MCP Captures Context

The Model Context Protocol captures several types of context from your dashboard:

1. **Dashboard Overview Context**:
   - Total number of products and resources
   - Number of active and completed products
   - Other key metrics visible on your dashboard

2. **View State Context**:
   - The current page or section you're viewing
   - Any filters you've applied
   - Search queries you've entered

3. **Visualization Context**:
   - Charts and graphs currently visible on your screen
   - Data being displayed in these visualizations

4. **User History Context**:
   - Your recent actions in the system
   - Pages you've recently visited
   - Changes you've recently made

5. **KPI Context** (when viewing KPI-related pages):
   - KPIs for the resource you're viewing
   - Recent KPI ratings and submissions
   - Performance trends

This context is collected automatically when you start a conversation and is updated each time you send a new message, ensuring that the AI Assistant always has the most current information about your dashboard state.

### Example Queries and Interactions

Here are some examples of how you can interact with the AI Assistant:

#### General Dashboard Queries:
- "What's the overall status of my dashboard?"
- "How many active projects do we have?"
- "Show me the resource utilization across all projects"
- "Give me a summary of the current quarter's progress"

#### Project-Specific Queries:
- "What's the automation status of Project X?"
- "Show me the projects with the lowest automation coverage"
- "Which projects are behind schedule?"
- "What's the regression percentage of the vflux project?"
- "Compare the smoke coverage between Project A and Project B"

#### Resource-Related Queries:
- "Which resources are assigned to Project Y?"
- "What resources are overallocated this quarter?"
- "Show me all resources with automation skills"
- "Who are the top 3 resources with the most project assignments?"
- "Which resources are available for new assignments next month?"

#### KPI-Related Queries:
- "Summarize the KPI ratings for [resource name]"
- "What's the average KPI rating for the team this month?"
- "Which resources have the highest ratings for [KPI name]?"
- "How have the KPI ratings for [resource name] changed over the last 3 months?"
- "Compare the KPI performance between the automation and manual testing teams"

#### Complex Multi-Part Queries:
- "Which projects have the lowest automation coverage and what resources are assigned to them?"
- "What's the relationship between resource allocation and project completion rates?"
- "Show me projects that are behind schedule but have high resource utilization"
- "Which resources are working on multiple high-priority projects with low automation coverage?"

#### Action Requests:
- "Create a new rock for [resource name]"
- "Schedule an automation update meeting for next Monday"
- "Add a leave for [resource name] from July 1 to July 15"
- "Remind me to follow up on the status of Project X next week"

#### Contextual Queries:
- "Why is this chart showing a decline?"
- "What does this KPI rating mean?"
- "Explain the data I'm seeing on this page"
- "What insights can you provide about the current view?"
- "What are the key trends in the data I'm looking at?"

### Advanced Usage Tips

#### 1. Be Specific
The more specific your question, the more helpful the AI Assistant can be. Include names, dates, and other details when relevant.

#### 2. Use Natural Language
You don't need to use special commands or syntax. Just ask your question in natural language, as you would to a human colleague.

#### 3. Follow-Up Questions
You can ask follow-up questions without repeating all the context. The AI Assistant remembers the conversation history.

#### 4. Combine Context Types
You can ask questions that combine different types of context, such as "Which resources assigned to Project X have the highest KPI ratings?"

#### 5. Request Explanations
If you don't understand something, ask the AI Assistant to explain it. For example, "Can you explain what this automation coverage metric means?"

### Managing Chat Sessions

#### Starting a New Chat
If you want to start a fresh conversation, click the "New Chat" button at the top of the chat interface. This will create a new chat session and collect fresh context from your current dashboard view.

#### Ending a Chat
When you're done with a conversation, you can click the "End Chat" button to mark the session as completed. This helps keep your chat history organized.

#### Viewing Chat History
You can view your past conversations by clicking on the "Chat History" link in the AI Assistant interface. This allows you to:
- Review previous conversations
- Continue where you left off in an active session
- See when each conversation took place
- Track how many messages were exchanged

### Troubleshooting

#### AI Assistant Not Responding
If the AI Assistant isn't responding to your messages:
1. Check your internet connection
2. Refresh the page
3. Try starting a new chat session
4. If the problem persists, contact your system administrator

#### Incorrect or Irrelevant Responses
If the AI Assistant is providing incorrect or irrelevant responses:
1. Try rephrasing your question to be more specific
2. Make sure you're on the relevant page for your query (e.g., if asking about KPIs, navigate to the KPI Management page)
3. Start a new chat session to refresh the context
4. Report the issue to your system administrator with details about what went wrong

#### Privacy and Data Security
The AI Assistant only has access to the data that you can see in your dashboard. It does not store your conversations permanently, and all context data is associated only with your user account.

### Limitations
While the AI Assistant is powerful, it does have some limitations:
- It can only access data that's available in the dashboard
- It may not be able to perform complex actions that require multiple steps
- It works best when you're specific about what you're asking
- It may not understand highly technical or domain-specific terminology that isn't part of the dashboard's vocabulary
