// Manual Updates Module JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize expandable content
    initExpandableContent();

    // Add event listeners for tab navigation
    initTabNavigation();
});

/**
 * Initialize expandable content functionality
 */
function initExpandableContent() {
    // Find all expandable content containers
    const expandableContainers = document.querySelectorAll('.expandable-content');

    expandableContainers.forEach(function(container) {
        // Create expand button if content is overflowing
        if (container.scrollHeight > container.clientHeight) {
            const expandButton = document.createElement('button');
            expandButton.className = 'expand-button';
            expandButton.innerHTML = '<i class="fas fa-chevron-down me-1"></i> Show More'; // Added icon for better visibility
            expandButton.setAttribute('aria-expanded', 'false');

            expandButton.addEventListener('click', function() {
                // Toggle expanded class
                container.classList.toggle('expanded');

                // Update button text and aria-expanded attribute
                if (container.classList.contains('expanded')) {
                    expandButton.innerHTML = '<i class="fas fa-chevron-up me-1"></i> Show Less'; // Changed icon direction
                    expandButton.setAttribute('aria-expanded', 'true');
                } else {
                    expandButton.innerHTML = '<i class="fas fa-chevron-down me-1"></i> Show More';
                    expandButton.setAttribute('aria-expanded', 'false');
                }

                // Scroll to ensure button is visible if content expanded
                if (container.classList.contains('expanded')) {
                    // Delay scrolling slightly to allow DOM to update
                    setTimeout(() => {
                        expandButton.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            });

            // Create a wrapper div for better positioning
            const buttonWrapper = document.createElement('div');
            buttonWrapper.className = 'text-center'; // Center the button
            buttonWrapper.appendChild(expandButton);

            // Insert button after the container
            container.parentNode.insertBefore(buttonWrapper, container.nextSibling);
        }
    });
}

/**
 * Initialize tab navigation
 */
function initTabNavigation() {
    // Find all tab navigation links
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');

    tabLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // If the link is to another page (not starting with #), let the default behavior happen
            const href = this.getAttribute('href');
            if (href && !href.startsWith('#') && !this.classList.contains('active')) {
                // This is a link to another page, let the default behavior happen
                // No need to prevent default or do anything else
                return;
            }

            // Only handle clicks on non-active tabs for same-page tabs
            if (!this.classList.contains('active')) {
                e.preventDefault();

                // Remove active class from all tabs
                tabLinks.forEach(function(tab) {
                    tab.classList.remove('active');
                });

                // Add active class to clicked tab
                this.classList.add('active');

                // Show corresponding tab content
                const targetId = href.split('#')[1];
                const tabContents = document.querySelectorAll('.tab-content .tab-pane');

                tabContents.forEach(function(content) {
                    content.classList.remove('show', 'active');
                });

                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.add('show', 'active');
                }
            }
        });
    });
}

/**
 * Format timeline badges based on their value
 */
function formatTimelineBadges() {
    const timelineBadges = document.querySelectorAll('.timeline-badge');

    timelineBadges.forEach(function(badge) {
        const text = badge.textContent.trim().toLowerCase();

        if (text.includes('immediate')) {
            badge.classList.add('immediate');
        } else if (text.includes('short')) {
            badge.classList.add('short');
        } else if (text.includes('medium')) {
            badge.classList.add('medium');
        } else if (text.includes('long')) {
            badge.classList.add('long');
        }
    });
}

/**
 * Initialize the meeting detail page
 */
function initMeetingDetailPage() {
    // Format timeline badges
    formatTimelineBadges();

    // Make meeting notes section scrollable if too long
    const notesSection = document.querySelector('.meeting-notes');
    if (notesSection && notesSection.scrollHeight > 500) {
        notesSection.style.maxHeight = '500px';
        notesSection.style.overflowY = 'auto';

        // Add a "View All" button
        const viewAllButton = document.createElement('button');
        viewAllButton.className = 'btn btn-sm btn-outline-primary mt-2';
        viewAllButton.textContent = 'View All Notes';
        viewAllButton.addEventListener('click', function() {
            if (notesSection.style.maxHeight === '500px') {
                notesSection.style.maxHeight = 'none';
                this.textContent = 'Collapse Notes';
            } else {
                notesSection.style.maxHeight = '500px';
                this.textContent = 'View All Notes';
            }
        });

        notesSection.parentNode.insertBefore(viewAllButton, notesSection.nextSibling);
    }
}

// Call specific initialization functions based on the current page
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the meeting detail page
    if (document.querySelector('.meeting-notes')) {
        initMeetingDetailPage();
    }

    // Format all timeline badges on the page
    formatTimelineBadges();
});
