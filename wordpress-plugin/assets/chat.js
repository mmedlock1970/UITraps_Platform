/**
 * UITraps AI Chat - Frontend JavaScript
 */
(function() {
    'use strict';

    let apiToken = null;
    let apiUrl = null;
    let conversationHistory = [];

    const elements = {
        container: document.getElementById('traps-ai-chat'),
        messages: document.getElementById('traps-ai-messages'),
        input: document.getElementById('traps-ai-input'),
        sendBtn: document.getElementById('traps-ai-send'),
        loading: document.getElementById('traps-ai-loading'),
        error: document.getElementById('traps-ai-error'),
    };

    // Check if chat container exists on page
    if (!elements.container) {
        return;
    }

    /**
     * Initialize chat
     */
    async function init() {
        // Check if user is logged in and has subscription
        if (!trapsAI.isLoggedIn) {
            showError('Please log in to use the AI assistant.');
            disableInput();
            return;
        }

        if (!trapsAI.hasSubscription) {
            showError('An active subscription is required to use the AI assistant.');
            disableInput();
            return;
        }

        // Get JWT token
        try {
            const response = await fetch(trapsAI.ajaxUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    action: 'traps_ai_get_token',
                    nonce: trapsAI.nonce,
                }),
            });

            const data = await response.json();

            if (data.success) {
                apiToken = data.data.token;
                apiUrl = data.data.apiUrl;
            } else {
                throw new Error(data.data?.message || 'Failed to authenticate');
            }
        } catch (error) {
            showError('Authentication failed: ' + error.message);
            disableInput();
            return;
        }

        // Set up event listeners
        elements.sendBtn.addEventListener('click', sendMessage);
        elements.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Auto-resize textarea
        elements.input.addEventListener('input', () => {
            elements.input.style.height = 'auto';
            elements.input.style.height = elements.input.scrollHeight + 'px';
        });
    }

    /**
     * Send message to AI
     */
    async function sendMessage() {
        const message = elements.input.value.trim();

        if (!message) {
            return;
        }

        if (!apiToken || !apiUrl) {
            showError('Not authenticated. Please refresh the page.');
            return;
        }

        // Add user message to UI
        addMessage(message, 'user');

        // Clear input
        elements.input.value = '';
        elements.input.style.height = 'auto';

        // Disable input while processing
        setLoading(true);

        try {
            const response = await fetch(`${apiUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiToken}`,
                },
                body: JSON.stringify({
                    message: message,
                    conversationHistory: conversationHistory,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();

            // Add assistant response to UI
            addMessage(data.response, 'assistant', data.sources);

            // Update conversation history
            conversationHistory.push(
                { role: 'user', content: message },
                { role: 'assistant', content: data.response }
            );

            // Limit conversation history to last 10 messages
            if (conversationHistory.length > 10) {
                conversationHistory = conversationHistory.slice(-10);
            }

        } catch (error) {
            console.error('Chat error:', error);
            showError('Failed to get response: ' + error.message);
            addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        } finally {
            setLoading(false);
        }
    }

    /**
     * Add message to chat UI
     */
    function addMessage(text, role, sources = []) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `traps-ai-message traps-ai-${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'traps-ai-avatar';
        avatar.textContent = role === 'user' ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'traps-ai-content';

        // Convert markdown-like formatting to HTML
        const formattedText = formatText(text);
        content.innerHTML = formattedText;

        // Add sources if available
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'traps-ai-sources';
            sourcesDiv.innerHTML = '<strong>Sources:</strong> ' +
                sources.map(url => `<a href="${url}" target="_blank" rel="noopener">${url}</a>`).join(', ');
            content.appendChild(sourcesDiv);
        }

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        elements.messages.appendChild(messageDiv);
        elements.messages.scrollTop = elements.messages.scrollHeight;
    }

    /**
     * Basic text formatting (markdown-like)
     */
    function formatText(text) {
        return text
            .split('\n\n')
            .map(para => {
                // Convert **bold** to <strong>
                para = para.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                // Convert *italic* to <em>
                para = para.replace(/\*(.+?)\*/g, '<em>$1</em>');
                // Convert `code` to <code>
                para = para.replace(/`(.+?)`/g, '<code>$1</code>');
                // Convert URLs to links
                para = para.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');

                return `<p>${para}</p>`;
            })
            .join('');
    }

    /**
     * Show loading state
     */
    function setLoading(isLoading) {
        elements.input.disabled = isLoading;
        elements.sendBtn.disabled = isLoading;
        elements.loading.style.display = isLoading ? 'flex' : 'none';

        if (!isLoading) {
            elements.input.focus();
        }
    }

    /**
     * Show error message
     */
    function showError(message) {
        elements.error.textContent = message;
        elements.error.style.display = 'block';
    }

    /**
     * Disable input (for unauthorized users)
     */
    function disableInput() {
        elements.input.disabled = true;
        elements.sendBtn.disabled = true;
        elements.input.placeholder = 'Chat unavailable';
    }

    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
