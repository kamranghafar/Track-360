/**
 * Chat interface functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const messagesContainer = document.getElementById('messages-container');
    const newChatButton = document.getElementById('new-chat-button');
    const endChatButton = document.getElementById('end-chat-button');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    // Send a message when the send button is clicked or Enter is pressed
    function setupMessageSending() {
        sendButton.addEventListener('click', sendMessage);

        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Send the message to the server
    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        // Display user message immediately
        addMessageToUI('user', message);

        // Clear input
        messageInput.value = '';

        // Send to server
        fetch(ChatConfig.endpoints.sendMessage(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.ai_message) {
                addMessageToUI('ai', data.ai_message.content);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToUI('system', 'Sorry, there was an error processing your message.');
        });
    }

    // Add a message to the UI
    function addMessageToUI(type, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Start a new chat
    function startNewChat() {
        fetch(ChatConfig.endpoints.newChat(), {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Clear messages
                messagesContainer.innerHTML = '';
                addMessageToUI('ai', 'Hello! How can I help you today?');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // End the current chat
    function endCurrentChat() {
        fetch(ChatConfig.endpoints.endChat(), {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addMessageToUI('system', 'This chat session has ended.');
                startNewChat();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    // Setup event listeners
    setupMessageSending();

    if (newChatButton) {
        newChatButton.addEventListener('click', startNewChat);
    }

    if (endChatButton) {
        endChatButton.addEventListener('click', endCurrentChat);
    }
});
