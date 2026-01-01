# Card Header Text Color Fix

## Issue Description
In the edit product update page, the heading in the card header with the classes "bg-primary text-white" was displaying white text, but it needed to be black for better visibility and design consistency.

## Solution
The solution was to change the text color from white to black by replacing the "text-white" class with "text-dark" class in the card header of the weekly_product_update_form.html template.

## Files Modified
1. `dashboard/templates/dashboard/weekly_product_update_form.html` - Changed the text color class from "text-white" to "text-dark"

## Technical Details
The specific change made was:

```html
<!-- Before -->
<div class="card-header bg-primary text-white">

<!-- After -->
<div class="card-header bg-primary text-dark">
```

This change ensures that the heading text "Update Product: [Product Name]" now appears in black instead of white, while maintaining the blue background of the card header.

## Benefits
- **Improved Readability**: Black text on the blue background provides better contrast and readability
- **Design Consistency**: The heading now matches the design requirements for the edit product update page
- **Specific Change**: The modification only affects the edit product update page, not other parts of the application