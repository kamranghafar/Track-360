# KPI Detail URL Fix

## Issue Description

The KPI Management module was experiencing a NoReverseMatch error when viewing a KPI's details:

```
NoReverseMatch at /dashboard/kpi-management/kpis/2/
Reverse for 'kpi-rating' with arguments '(80, '', '')' not found. 1 pattern(s) tried: ['dashboard/kpi\\-management/resources/(?P<resource_id>[0-9]+)/rate/(?P<year>[0-9]+)/(?P<month>[0-9]+)/\\Z']
```

This error occurred because the template was trying to generate a URL for the "Rate Now" and "Add Rating" buttons using the `{% url 'kpi-rating' kpi.resource.id current_year current_month %}` tag, but the `current_year` and `current_month` variables were not defined in the context.

## Root Cause

The KPIDetailView class was not setting the `current_year` and `current_month` variables in its get_context_data method, unlike other views such as ResourceKPIListView which do set these variables. This caused Django to try to reverse the URL with empty strings instead of numeric values, resulting in the NoReverseMatch error.

## Solution

The solution was to update the KPIDetailView's get_context_data method to include the current_year and current_month variables in the context:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    # Get all ratings for this KPI
    context['ratings'] = self.object.ratings.all().order_by('-year', '-month')

    # Calculate average rating
    if context['ratings'].exists():
        context['avg_rating'] = context['ratings'].aggregate(Avg('rating'))['rating__avg']
    else:
        context['avg_rating'] = None
        
    # Get current month and year for rating link
    today = timezone.now().date()
    context['current_month'] = today.month
    context['current_year'] = today.year

    return context
```

By adding these variables to the context, the template can now generate the correct URL for the "Rate Now" and "Add Rating" buttons.

## Benefits

1. Fixes the NoReverseMatch error when viewing KPI details
2. Ensures consistent behavior with other views in the KPI Management module
3. Improves user experience by allowing users to rate KPIs directly from the KPI detail page
4. Maintains the expected functionality of the "Rate Now" and "Add Rating" buttons