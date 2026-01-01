# KPI Form Field Error Fix

## Issue Description

The KPI Management module was experiencing a ValueError when submitting KPI ratings:

```
ValueError at /dashboard/kpi-management/resources/80/rate/2025/7/
'KPIRatingForm' has no field named 'month'.
```

This error occurred in the Django forms.py file, line 301, in the add_error method. The issue was that the model validation was trying to add an error to a field named 'month' in the KPIRatingForm, but that field doesn't exist in the form.

## Root Cause

The KPIRatingForm only includes the 'rating' and 'remarks' fields, but not the 'month' and 'year' fields:

```python
class KPIRatingForm(forms.ModelForm):
    class Meta:
        model = KPIRating
        fields = ['rating', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
```

However, the KPIRating model's clean method validates the 'month' and 'year' fields:

```python
def clean(self):
    from django.core.exceptions import ValidationError
    if self.month is None:
        raise ValidationError({'month': 'Month is required'})
    if self.month < 1 or self.month > 12:
        raise ValidationError({'month': 'Month must be between 1 and 12'})
    if self.year is None:
        raise ValidationError({'year': 'Year is required'})
    # ...
```

In the KPIRatingView's post method, the form was being validated first, and then the 'month' and 'year' values were being set on the model instance after validation. If the model validation failed for the 'month' field, it would try to add the error to the form field, but the form doesn't have a 'month' field, causing the ValueError.

## Solution

The solution was to set the 'month', 'year', and 'kpi' values on the form instance before validation:

```python
# Set month and year before validation to avoid form field errors
rating = form.instance
rating.kpi = kpi
rating.month = month
rating.year = year

if form.is_valid():
    form.save()
else:
    all_valid = False
```

By setting these values before validation, we ensure that the model validation won't fail due to missing 'month' or 'year' values, and if there are any validation errors for these fields, they won't be added to the form (since the form doesn't have these fields).

## Benefits

1. Prevents ValueError when submitting KPI ratings
2. Maintains the separation of concerns between the form and the model
3. Ensures that the model validation still occurs for all fields
4. Simplifies the form by only including the fields that the user needs to interact with