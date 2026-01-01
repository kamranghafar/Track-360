# Dashboard Error Fix

## Issue
The dashboard page was throwing a NoReverseMatch error:
```
NoReverseMatch at /dashboard/
Reverse for 'records-list' not found. 'records-list' is not a valid view function or pattern name.
```

## Cause
The error occurred because:
1. The URL patterns for the Records section were commented out in `urls.py` as part of hiding the Records section
2. However, the navigation link in `base.html` still contained a Django template tag `{% url 'records-list' %}` inside an HTML comment
3. Django still processes template tags inside HTML comments, causing it to try to resolve the 'records-list' URL

## Solution
The solution was to properly comment out the Django template tag in `base.html` by:
1. Replacing the HTML comments (`<!-- -->`) with Django template comments (`{% comment %}` and `{% endcomment %}`)
2. As an additional safety measure, replacing `{% url 'records-list' %}` with a simple `#` placeholder

### Changes Made
In `dashboard/templates/dashboard/base.html`:

**Before:**
```html
<!-- Records section temporarily hidden
<a href="{% url 'records-list' %}" class="{% if '/records/' in request.path %}active{% endif %}">
    <span class="sidebar-icon"><i class="fas fa-trash-restore"></i></span>
    <span class="sidebar-text">Records</span>
</a>
-->
```

**After:**
```html
{% comment %}
<!-- Records section temporarily hidden -->
<a href="#" class="{% if '/records/' in request.path %}active{% endif %}">
    <span class="sidebar-icon"><i class="fas fa-trash-restore"></i></span>
    <span class="sidebar-text">Records</span>
</a>
{% endcomment %}
```

## Why This Works
HTML comments (`<!-- -->`) don't prevent Django from processing template tags within them. Django template comments (`{% comment %}` and `{% endcomment %}`) properly tell Django to ignore everything between them, including template tags.

This fix ensures that Django doesn't try to resolve the 'records-list' URL when rendering the dashboard page, while still maintaining the commented-out state of the Records section.