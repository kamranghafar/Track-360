# Quarter Summary Notes Fix

## Issue
In the Quarter Summary view, users were unable to see the full notes for targets and achievements because they were being truncated to 50 characters.

## Solution
I made the following changes to the `quarter_summary.html` template:

1. Removed the `truncatechars:50` filter from the target description display:
   ```html
   <!-- Before -->
   <td>{{ target.target_description|truncatechars:50 }}</td>
   
   <!-- After -->
   <td style="white-space: pre-wrap; max-width: 300px;">{{ target.target_description }}</td>
   ```

2. Removed the `truncatechars:50` filter from the achievement notes display:
   ```html
   <!-- Before -->
   <td>{{ target.achievement_notes|default:"-"|truncatechars:50 }}</td>
   
   <!-- After -->
   <td style="white-space: pre-wrap; max-width: 300px;">{{ target.achievement_notes|default:"-" }}</td>
   ```

3. Added CSS styling to ensure that long text wraps properly and doesn't break the table layout:
   - `white-space: pre-wrap` - Preserves line breaks and spaces
   - `max-width: 300px` - Limits the width of the cell to prevent the table from becoming too wide

These changes allow users to see the full notes in the Quarter Summary while maintaining a clean and readable layout.