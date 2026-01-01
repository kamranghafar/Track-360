# KPI View Error Fix

## Issue Description

The KPI Management module was experiencing a ValueError when viewing KPI ratings:

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

In the KPIRatingView's get_context_data method, when creating a new form instance (when there's no existing rating), it wasn't setting the 'month', 'year', and 'kpi' values on the form instance. If the model validation was triggered during form initialization or when accessing certain properties, it would try to add errors to the form fields, but the form doesn't have these fields, causing the ValueError.

## Solution

The solution was to set the 'month', 'year', and 'kpi' values on the form instance when creating a new form in the get_context_data method:

```python
if rating:
    form = KPIRatingForm(instance=rating, prefix=f'kpi_{kpi.id}')
else:
    form = KPIRatingForm(prefix=f'kpi_{kpi.id}')
    
# Set month, year, and kpi on the form instance to avoid validation errors
if not rating:
    form.instance.kpi = kpi
    form.instance.month = month
    form.instance.year = year
```

By setting these values before any validation might occur, we ensure that the model validation won't fail due to missing 'month', 'year', or 'kpi' values, and if there are any validation errors for these fields, they won't be added to the form (since the form doesn't have these fields).

## Benefits

1. Prevents ValueError when viewing KPI ratings
2. Maintains the separation of concerns between the form and the model
3. Ensures that the model validation still occurs for all fields
4. Simplifies the form by only including the fields that the user needs to interact with
5. Provides a consistent approach with the post method, which already had a similar fix