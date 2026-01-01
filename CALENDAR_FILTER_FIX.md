# Resource Planning Calendar View Filter Fix

## Issue
In the Resource Planning calendar view tab, when the user applies a filter, the data was not updating correctly in the calendar view.

## Root Cause
The issue was in the `filterCalendar` function in the `resource_planning.html` template. After applying filters to the events by setting their display property, the function was using `calendar.updateSize()` to refresh the calendar. However, `updateSize()` only updates the size of the calendar container, not the events themselves.

According to the FullCalendar documentation, `calendar.render()` should be used to fully re-render the calendar after making changes to events. This ensures that the filtered events are properly displayed or hidden.

## Solution
Modified the `filterCalendar` function to use `calendar.render()` instead of `calendar.updateSize()` to properly refresh the calendar view after applying filters.

### Changes Made
1. Replaced `calendar.updateSize()` with `calendar.render()` in the `filterCalendar` function
2. Added a console log statement for debugging purposes

## File Changed
- `dashboard/templates/dashboard/resource_planning.html`

## Testing
The fix can be tested by:
1. Navigate to the Resource Planning page
2. Click on the Calendar View tab
3. Apply filters using the dropdown menus (Resource, Project, Lead)
4. Verify that the calendar view updates correctly to show only the filtered events