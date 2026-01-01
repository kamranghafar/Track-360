# KPI Rating TypeError Fix

## Issue Description

The KPI Management module was experiencing a TypeError when submitting KPI ratings:

```
TypeError at /dashboard/kpi-management/resources/80/rate/2025/7/
'<' not supported between instances of 'NoneType' and 'int'
```

This error occurred in the `clean` method of the `KPIRating` model at line 887 in `models.py`. The issue was that the code was trying to compare `None` values with integers, which is not supported in Python.

## Root Cause

The validation logic in both the `KPIRating` and `KPIRatingSubmission` models was not checking if the `month`, `year`, or `rating` fields were `None` before performing comparisons with integers. This could happen when a form was submitted with empty values for these fields.

## Solution

The fix involved updating the `clean` methods in both models to check if the fields are `None` before performing any comparisons:

1. In the `KPIRating` model:
   - Added a check for `self.month is None`
   - Added a check for `self.year is None`
   - Added a check for `self.rating is None`

2. In the `KPIRatingSubmission` model:
   - Added a check for `self.month is None`
   - Added a check for `self.year is None`

## Code Changes

### KPIRating.clean method (before):

```python
def clean(self):
    from django.core.exceptions import ValidationError
    if self.month < 1 or self.month > 12:
        raise ValidationError({'month': 'Month must be between 1 and 12'})
    if self.rating < 1 or self.rating > 5:
        raise ValidationError({'rating': 'Rating must be between 1 and 5'})
```

### KPIRating.clean method (after):

```python
def clean(self):
    from django.core.exceptions import ValidationError
    if self.month is None:
        raise ValidationError({'month': 'Month is required'})
    if self.month < 1 or self.month > 12:
        raise ValidationError({'month': 'Month must be between 1 and 12'})
    if self.year is None:
        raise ValidationError({'year': 'Year is required'})
    if self.rating is None:
        raise ValidationError({'rating': 'Rating is required'})
    if self.rating < 1 or self.rating > 5:
        raise ValidationError({'rating': 'Rating must be between 1 and 5'})
```

### KPIRatingSubmission.clean method (before):

```python
def clean(self):
    from django.core.exceptions import ValidationError
    if self.month < 1 or self.month > 12:
        raise ValidationError({'month': 'Month must be between 1 and 12'})
    if not self.overall_remarks:
        raise ValidationError({'overall_remarks': 'Overall remarks are required'})
```

### KPIRatingSubmission.clean method (after):

```python
def clean(self):
    from django.core.exceptions import ValidationError
    if self.month is None:
        raise ValidationError({'month': 'Month is required'})
    if self.month < 1 or self.month > 12:
        raise ValidationError({'month': 'Month must be between 1 and 12'})
    if self.year is None:
        raise ValidationError({'year': 'Year is required'})
    if not self.overall_remarks:
        raise ValidationError({'overall_remarks': 'Overall remarks are required'})
```

## Benefits

1. Prevents TypeError when comparing None with integers
2. Provides more specific error messages to users when required fields are missing
3. Ensures consistent validation across both models
4. Improves the robustness of the KPI rating submission process