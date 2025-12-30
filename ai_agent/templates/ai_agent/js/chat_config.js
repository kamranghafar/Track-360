/**
 * Chat configuration script
 * Provides dynamic configuration for chat API endpoints
 */

const ChatConfig = {
    // Get base URL from the host of the current page
    baseUrl: window.location.protocol + '//' + window.location.host,

    // API endpoints
    endpoints: {
        sendMessage: function() { return this.baseUrl + '/ai_agent/api/send-message/'; },
        endChat: function() { return this.baseUrl + '/ai_agent/api/end-chat/'; },
        newChat: function() { return this.baseUrl + '/ai_agent/api/new-chat/'; }
    }
};
