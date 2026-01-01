// Extension Patch Script
// This script helps prevent errors from browser extensions that might interact with our site

// Function to patch potential issues with browser extensions
(function() {
    // Create a more comprehensive patch for the contentScript.js issue
    // This needs to run as early as possible in the page lifecycle

    // Define a global record function that contentScript.js might be looking for
    window.record = function(data) {
        // Safely handle the data to prevent errors
        if (!data) return { sentence: '' };

        // If data exists but sentence doesn't, add it
        if (typeof data === 'object' && !data.sentence) {
            data.sentence = '';
        }

        return data;
    };

    // Also patch any potential parent objects that might be used
    window.__extensionPatch = {
        record: window.record
    };

    // Store original addEventListener method
    var originalAddEventListener = EventTarget.prototype.addEventListener;

    // Track if we're currently processing a mouse event to prevent recursive handling
    var processingMouseEvent = false;

    // Store original dispatchEvent method
    var originalDispatchEvent = EventTarget.prototype.dispatchEvent;

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

    // Override addEventListener to ensure modal events are not blocked
    EventTarget.prototype.addEventListener = function(type, listener, options) {
        // For mouse events on modals, ensure they don't cause blinking
        if ((type === 'mouseover' || type === 'mousemove' || type === 'mouseenter') && 
            (this.classList && this.classList.contains('modal'))) {

            // Wrap the listener to prevent rapid re-triggering
            var wrappedListener = function(event) {
                // Only call the original listener if we're not already processing a mouse event
                if (!processingMouseEvent) {
                    processingMouseEvent = true;
                    listener.call(this, event);
                    setTimeout(function() {
                        processingMouseEvent = false;
                    }, 50); // Debounce mouse events
                }
            };

            // Call the original method with our wrapped listener
            return originalAddEventListener.call(this, type, wrappedListener, options);
        }

        // Call the original method for non-mouse events or non-modal elements
        return originalAddEventListener.call(this, type, listener, options);
    };

    // Intercept Promise rejections which might be related to the extension
    window.addEventListener('unhandledrejection', function(event) {
        // Check if the error is related to the sentence property
        if (event.reason && event.reason.message && 
            (event.reason.message.includes("Cannot read properties of undefined (reading 'sentence')") ||
             event.reason.message.includes("Cannot read property 'sentence' of undefined"))) {

            // Prevent the error from propagating
            event.preventDefault();
            console.warn('Prevented unhandled promise rejection:', event.reason.message);
        }
    });

    // Listen for errors and prevent them from affecting the main application
    window.addEventListener('error', function(event) {
        // Check if the error is related to contentScript.js or the sentence property
        // Exclude errors related to modal functionality
        if (((event.filename && event.filename.includes('contentScript.js')) ||
             (event.message && event.message.includes("'sentence'"))) &&
            !(event.message && (
                event.message.includes('modal') || 
                event.message.includes('tab') || 
                event.message.includes('form')
            ))) {

            // Prevent the error from propagating
            event.preventDefault();
            console.warn('Prevented error from extension:', event.message);
        }
    });

    // Ensure Bootstrap's modal functionality works
    document.addEventListener('DOMContentLoaded', function() {
        // Fix for modal not being clickable and prevent blinking
        var fixModals = function() {
            var modals = document.querySelectorAll('.modal');
            modals.forEach(function(modal) {
                // Ensure the modal is clickable
                modal.style.pointerEvents = 'auto';

                // Prevent blinking by disabling unnecessary repaints
                modal.style.backfaceVisibility = 'hidden';
                modal.style.transform = 'translateZ(0)';
                modal.style.perspective = '1000px';

                // Ensure form elements inside the modal are clickable
                var formElements = modal.querySelectorAll('input, select, textarea, button, .nav-link, .tab-pane');
                formElements.forEach(function(element) {
                    element.style.pointerEvents = 'auto';

                    // Also apply the same anti-blinking properties
                    element.style.backfaceVisibility = 'hidden';
                    element.style.transform = 'translateZ(0)';
                    element.style.perspective = '1000px';
                });

                // Add a specific handler for mouse events on the modal
                modal.addEventListener('mousemove', function(e) {
                    // This empty handler with the stopPropagation prevents event bubbling
                    // that might cause the blinking
                    e.stopPropagation();
                }, true);
            });
        };

        // Run the fix immediately and after a short delay to ensure it applies
        fixModals();
        setTimeout(fixModals, 500);

        // Also run the fix when a modal is shown
        document.body.addEventListener('shown.bs.modal', fixModals);
    });

    console.info('Enhanced extension patch script loaded with anti-blinking protection');
})();
