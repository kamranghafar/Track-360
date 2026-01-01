// Enhanced Rich Text Editor with Modern UI/UX
document.addEventListener('DOMContentLoaded', function() {
    // Find all textareas with name="notes" or name="latest_project_updates"
    // Exclude textareas inside modal dialogs to prevent blinking issues
    const allTextareas = document.querySelectorAll('textarea[name="notes"], textarea[name="latest_project_updates"]');

    // Filter out textareas that are inside modal dialogs
    const textareas = Array.from(allTextareas).filter(textarea => {
        let parent = textarea.parentElement;
        while (parent !== null) {
            if (parent.classList.contains('modal') || 
                (parent.id && parent.id.startsWith('editModal'))) {
                return false;
            }
            parent = parent.parentElement;
        }
        return true;
    });

    // Initialize rich text editors for textareas
    initRichTextEditors(textareas);

    // Add event listener for modal shown event to initialize rich text editors in modals
    document.addEventListener('shown.bs.modal', function(event) {
        // Find textareas inside the opened modal
        const modalTextareas = event.target.querySelectorAll('textarea[name="notes"], textarea[name="latest_project_updates"]');
        // Initialize rich text editors for modal textareas
        if (modalTextareas.length > 0) {
            initRichTextEditors(modalTextareas);
        }
    });
});

// Function to initialize rich text editors for given textareas
function initRichTextEditors(textareas) {
    textareas.forEach(function(textarea) {
        // Skip if this textarea already has a rich text editor
        if (textarea.hasAttribute('data-rich-text-initialized')) {
            return;
        }

        // Mark this textarea as initialized
        textarea.setAttribute('data-rich-text-initialized', 'true');
        // Create the editor container with modern styling
        const editorContainer = document.createElement('div');
        editorContainer.className = 'rich-text-editor-container';

        // Create the toolbar with improved layout
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar';

        // Create toolbar groups for better organization
        const formatGroup = document.createElement('div');
        formatGroup.className = 'toolbar-group';

        const paragraphGroup = document.createElement('div');
        paragraphGroup.className = 'toolbar-group';

        const listGroup = document.createElement('div');
        listGroup.className = 'toolbar-group';

        const alignGroup = document.createElement('div');
        alignGroup.className = 'toolbar-group';

        const indentGroup = document.createElement('div');
        indentGroup.className = 'toolbar-group';

        const linkGroup = document.createElement('div');
        linkGroup.className = 'toolbar-group';

        // Create the editable content area with improved styling
        const editor = document.createElement('div');
        editor.className = 'rich-text-editor';
        editor.contentEditable = true;
        editor.innerHTML = textarea.value; // Set initial content from textarea
        editor.setAttribute('placeholder', 'Enter your text here...');

        // Add a character counter for better UX
        const counterContainer = document.createElement('div');
        counterContainer.className = 'editor-counter';
        const counter = document.createElement('span');
        counter.textContent = `${editor.textContent.length} characters`;
        counterContainer.appendChild(counter);

        // Hide the original textarea and its label if it's in a form-floating container
        textarea.style.display = 'none';

        // Check if the textarea is in a form-floating container and hide the label
        const formFloating = textarea.closest('.form-floating');
        if (formFloating) {
            const label = formFloating.querySelector('label[for="' + textarea.id + '"]');
            if (label) {
                label.style.display = 'none';
            }
        }

        // Enhanced toolbar buttons with better grouping and tooltips
        const buttons = [
            // Text formatting group
            { group: formatGroup, command: 'bold', icon: 'fas fa-bold', title: 'Bold (Ctrl+B)' },
            { group: formatGroup, command: 'italic', icon: 'fas fa-italic', title: 'Italic (Ctrl+I)' },
            { group: formatGroup, command: 'underline', icon: 'fas fa-underline', title: 'Underline (Ctrl+U)' },
            { group: formatGroup, command: 'removeFormat', icon: 'fas fa-eraser', title: 'Clear Formatting' },

            // Paragraph formatting group
            { group: paragraphGroup, command: 'formatBlock', value: 'h1', icon: 'fas fa-heading', title: 'Heading 1' },
            { group: paragraphGroup, command: 'formatBlock', value: 'h2', icon: 'fas fa-heading', title: 'Heading 2', className: 'fa-xs' },
            { group: paragraphGroup, command: 'formatBlock', value: 'h3', icon: 'fas fa-heading', title: 'Heading 3', className: 'fa-xs' },
            { group: paragraphGroup, command: 'formatBlock', value: 'p', icon: 'fas fa-paragraph', title: 'Paragraph' },

            // List group
            { group: listGroup, command: 'insertUnorderedList', icon: 'fas fa-list-ul', title: 'Bullet List' },
            { group: listGroup, command: 'insertOrderedList', icon: 'fas fa-list-ol', title: 'Numbered List' },

            // Alignment group
            { group: alignGroup, command: 'justifyLeft', icon: 'fas fa-align-left', title: 'Align Left' },
            { group: alignGroup, command: 'justifyCenter', icon: 'fas fa-align-center', title: 'Align Center' },
            { group: alignGroup, command: 'justifyRight', icon: 'fas fa-align-right', title: 'Align Right' },
            { group: alignGroup, command: 'justifyFull', icon: 'fas fa-align-justify', title: 'Justify' },

            // Indentation group
            { group: indentGroup, command: 'indent', icon: 'fas fa-indent', title: 'Indent' },
            { group: indentGroup, command: 'outdent', icon: 'fas fa-outdent', title: 'Outdent' },

            // Link group
            { group: linkGroup, command: 'createLink', icon: 'fas fa-link', title: 'Insert Link' },
            { group: linkGroup, command: 'unlink', icon: 'fas fa-unlink', title: 'Remove Link' }
        ];

        buttons.forEach(function(button) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'toolbar-button';
            btn.title = button.title;
            btn.setAttribute('data-command', button.command);
            if (button.value) {
                btn.setAttribute('data-value', button.value);
            }

            const icon = document.createElement('i');
            icon.className = button.icon;
            if (button.className) {
                icon.classList.add(button.className);
            }

            btn.appendChild(icon);

            // Add active state for buttons that can be toggled
            if (['bold', 'italic', 'underline'].includes(button.command)) {
                btn.addEventListener('mousedown', function(e) {
                    e.preventDefault(); // Prevent focus loss
                });
            }

            btn.addEventListener('click', function(e) {
                e.preventDefault();

                if (button.command === 'createLink') {
                    // Enhanced link dialog
                    const selection = window.getSelection();
                    if (selection.toString().length === 0) {
                        alert('Please select the text you want to convert to a link first.');
                        return;
                    }

                    const url = prompt('Enter the URL:', 'https://');
                    if (url && url !== 'https://') {
                        document.execCommand(button.command, false, url);
                    }
                } else if (button.value) {
                    document.execCommand(button.command, false, button.value);
                } else {
                    document.execCommand(button.command, false, null);
                }

                // Update button active states
                updateActiveButtons();

                // Update the hidden textarea with the editor content
                updateTextarea();

                // Focus back on the editor
                editor.focus();
            });

            // Add button to its group
            button.group.appendChild(btn);
        });

        // Add all groups to the toolbar
        toolbar.appendChild(formatGroup);
        toolbar.appendChild(paragraphGroup);
        toolbar.appendChild(listGroup);
        toolbar.appendChild(alignGroup);
        toolbar.appendChild(indentGroup);
        toolbar.appendChild(linkGroup);

        // Function to update the textarea with the editor content
        function updateTextarea() {
            textarea.value = editor.innerHTML;
            // Update character counter
            counter.textContent = `${editor.textContent.length} characters`;
        }

        // Function to update active state of buttons based on current selection
        function updateActiveButtons() {
            const buttons = toolbar.querySelectorAll('.toolbar-button');
            buttons.forEach(function(button) {
                const command = button.getAttribute('data-command');
                if (['bold', 'italic', 'underline'].includes(command)) {
                    if (document.queryCommandState(command)) {
                        button.classList.add('active');
                    } else {
                        button.classList.remove('active');
                    }
                }
            });
        }

        // Update textarea when editor content changes
        editor.addEventListener('input', updateTextarea);
        editor.addEventListener('blur', updateTextarea);

        // Update active buttons when selection changes
        editor.addEventListener('mouseup', updateActiveButtons);
        editor.addEventListener('keyup', updateActiveButtons);

        // Add keyboard shortcuts
        editor.addEventListener('keydown', function(e) {
            if (e.ctrlKey) {
                switch(e.key.toLowerCase()) {
                    case 'b':
                        e.preventDefault();
                        document.execCommand('bold', false, null);
                        updateActiveButtons();
                        break;
                    case 'i':
                        e.preventDefault();
                        document.execCommand('italic', false, null);
                        updateActiveButtons();
                        break;
                    case 'u':
                        e.preventDefault();
                        document.execCommand('underline', false, null);
                        updateActiveButtons();
                        break;
                }
            }
        });

        // Add the toolbar and editor to the container
        editorContainer.appendChild(toolbar);
        editorContainer.appendChild(editor);
        editorContainer.appendChild(counterContainer);

        // Insert the editor container after the textarea
        textarea.parentNode.insertBefore(editorContainer, textarea.nextSibling);

        // Initialize active buttons
        updateActiveButtons();
    });
}
