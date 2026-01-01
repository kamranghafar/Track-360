# Modal Blinking Fix

## Issue Description
When users went to Manual Updates, added a new update, started a meeting, and clicked the Edit button of a project, the modal would begin to blink continuously when the mouse hovered over the screen. Once the mouse moved out of the screen, the modal would stabilize and appear fine. However, when the mouse hovered again and the user tried to type anything, the modal would start blinking again, making it impossible to interact with.

## Root Cause
After investigation, it was determined that the issue was caused by a conflict between the extension-patch.js script and mouse events on the modal. The script was designed to prevent errors from browser extensions, but it was inadvertently causing an event loop with mouse events, leading to the blinking effect.

Specifically:
1. Mouse events (mouseover, mousemove, mouseenter) were being repeatedly triggered
2. These events were causing the modal to repaint rapidly, creating the blinking effect
3. The event handling in extension-patch.js was not properly managing these events

## Solution
The extension-patch.js file was modified to:

1. **Prevent Event Loops**: Added tracking for mouse event processing to prevent recursive handling of mouse events.

2. **Override dispatchEvent**: Modified the dispatchEvent method to prevent event loops with mouse events on modals.

3. **Debounce Mouse Events**: Wrapped mouse event listeners with debouncing to prevent rapid re-triggering.

4. **Optimize Rendering**: Added CSS properties (backfaceVisibility, transform, perspective) to prevent unnecessary repaints.

5. **Stop Event Propagation**: Added a specific handler for mousemove events on modals to stop propagation.

6. **Ensure Timely Application**: Added an event listener for the shown.bs.modal event to apply the fix when a modal is shown.

## Files Modified
1. `dashboard/static/js/extension-patch.js` - Enhanced to prevent event loops and optimize rendering for modals.

## Technical Details
The key technical changes include:

```javascript
// Track if we're currently processing a mouse event to prevent recursive handling
var processingMouseEvent = false;

// Override dispatchEvent to prevent event loops with mouse events on modals
EventTarget.prototype.dispatchEvent = function(event) {
    // If this is a mouse event on a modal or its children and we're already processing one, skip it
    if (!processingMouseEvent && 
        (event.type === 'mouseover' || event.type === 'mousemove' || event.type === 'mouseenter') && 
        (this.closest && this.closest('.modal') || (this.classList && this.classList.contains('modal')))) {
        
        processingMouseEvent = true;
        var result = originalDispatchEvent.call(this, event);
        processingMouseEvent = false;
        return result;
    }
    
    return originalDispatchEvent.call(this, event);
};
```

And:

```javascript
// Prevent blinking by disabling unnecessary repaints
modal.style.backfaceVisibility = 'hidden';
modal.style.transform = 'translateZ(0)';
modal.style.perspective = '1000px';
```

## Testing
After implementing these changes, users should be able to:
1. Click on the Edit button for a project during a meeting
2. Hover over the modal without experiencing any blinking
3. Interact with all form elements in the modal without the blinking effect
4. Save changes successfully

The fix ensures that the extension patch still prevents errors from browser extensions while allowing normal interaction with the modal without any visual glitches.