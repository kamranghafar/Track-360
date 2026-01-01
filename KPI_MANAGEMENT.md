# KPI Management Module

## Overview

The KPI Management module allows users to define, track, and rate Key Performance Indicators (KPIs) for resources. This module provides a structured way to evaluate resource performance on a monthly basis using a 1-5 rating scale.

## Features

- **KPI Definition**: Create and manage KPIs for each resource
- **Monthly Ratings**: Rate KPIs on a scale of 1-5 for each month
- **Optional Remarks**: Add remarks for each KPI rating
- **Overall Remarks**: Provide mandatory overall remarks when submitting ratings
- **Rating History**: View historical ratings for each KPI
- **Submission History**: Track all rating submissions by month/year

## Models

### KPI

Stores the definition of Key Performance Indicators for resources.

- **resource**: ForeignKey to Resource
- **name**: Name of the KPI
- **description**: Detailed description of the KPI (optional)
- **created_at**: Timestamp when the KPI was created
- **updated_at**: Timestamp when the KPI was last updated

### KPIRating

Stores monthly ratings for KPIs.

- **kpi**: ForeignKey to KPI
- **month**: Month (1-12)
- **year**: Year (e.g., 2023)
- **rating**: Rating from 1 to 5
- **remarks**: Optional remarks for this KPI rating
- **created_at**: Timestamp when the rating was created
- **updated_at**: Timestamp when the rating was last updated

### KPIRatingSubmission

Stores overall remarks for a set of KPI ratings submitted together.

- **resource**: ForeignKey to Resource
- **month**: Month (1-12)
- **year**: Year (e.g., 2023)
- **overall_remarks**: Mandatory overall remarks for this submission
- **submitted_by**: ForeignKey to User
- **submitted_at**: Timestamp when the submission was created
- **updated_at**: Timestamp when the submission was last updated

## Rating Scale

The KPI rating scale is defined as follows:

1. **Poor**: Performance is significantly below expectations
2. **Below Expectations**: Performance is somewhat below expectations
3. **Meets Expectations**: Performance meets expectations
4. **Exceeds Expectations**: Performance exceeds expectations
5. **Outstanding**: Performance is exceptional and far exceeds expectations

## User Interface

### KPI Management Main Page

The main page displays a list of all resources with their KPI counts. From here, users can:
- View KPIs for a specific resource
- Rate KPIs for the current or previous month

### Resource KPI List

This page displays all KPIs for a specific resource. Users can:
- Add new KPIs
- View, edit, or delete existing KPIs
- Rate KPIs for the current month
- View submission history

### KPI Detail Page

This page displays detailed information about a specific KPI, including:
- KPI name and description
- Average rating
- Rating history

### KPI Rating Page

This page allows users to rate all KPIs for a specific resource for a specific month/year. Users must:
- Rate each KPI on a scale of 1-5
- Optionally provide remarks for each KPI
- Provide mandatory overall remarks for the submission

### KPI Submission History

This page displays a list of all KPI rating submissions for a specific resource. Users can:
- View submission details
- Edit ratings for a specific submission

### KPI Submission Detail

This page displays detailed information about a specific KPI rating submission, including:
- Submission information (resource, period, submitted by, submission date)
- Average rating
- Overall remarks
- Individual KPI ratings and remarks

## Workflow

1. **Define KPIs**: Create KPIs for each resource
2. **Rate KPIs**: Rate KPIs for each resource on a monthly basis
3. **Review Ratings**: Review historical ratings to track performance over time

## Access

The KPI Management module is accessible from the main navigation sidebar. Users can click on "KPI Management" to access the module.