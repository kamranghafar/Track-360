/**
 * This script prevents certain browser extension errors by defining expected globals
 */

// Prevent errors from Chrome extensions like 'extension-patch.js'
document.addEventListener('DOMContentLoaded', function() {
    // Define a no-op function for extension error suppression
    window.__extensionPatchSuppress = function() {
        return true;
    };

    // If chartColorPalette is referenced before definition, provide an empty object
    if (typeof window.chartColorPalette === 'undefined') {
        window.chartColorPalette = {
            primary: [],
            secondary: [],
            border: []
        };
    }

    // Console message to indicate error suppression is active
    console.debug('Extension error suppression active');
});
