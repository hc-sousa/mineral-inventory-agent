document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const mineralForm = document.getElementById('mineral-form');
    const resetFormButton = document.getElementById('reset-form');
    const sendButton = document.getElementById('send-button');
    
    // Track conversation history
    let conversationHistory = [];
    
    // Track form changes for revert functionality
    let formChangeHistory = [];
    let currentFormState = {};
    
    // Create revert button
    const revertButton = document.createElement('button');
    revertButton.id = 'revert-changes';
    revertButton.className = 'revert-button';
    revertButton.textContent = 'Revert Changes';
    revertButton.style.display = 'none'; // Hide by default
    document.body.appendChild(revertButton);
    
    // Set up marked.js options
    marked.setOptions({
        breaks: true,         // Add line breaks as <br>
        gfm: true,            // Use GitHub Flavored Markdown
        headerIds: false      // Don't add IDs to headers
    });
    
    // Save initial form state
    saveFormState();

    // Function to show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        // Add three bouncing dots
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingDiv.appendChild(dot);
        }
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Function to hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Function to set the button to loading state
    function setButtonLoading(isLoading) {
        if (isLoading) {
            sendButton.classList.add('loading');
            sendButton.disabled = true;
            userInput.disabled = true;
        } else {
            sendButton.classList.remove('loading');
            sendButton.disabled = false;
            userInput.disabled = false;
            userInput.focus();
        }
    }

    // Function to add a message to the chat interface
    function addMessage(content, type, isHistory = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = type;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Parse markdown for bot messages, but keep plain text for user messages
        if (type === 'bot-message' || type === 'system-message') {
            // Parse markdown and sanitize HTML if DOMPurify is available
            messageContent.innerHTML = window.DOMPurify ? 
                DOMPurify.sanitize(marked.parse(content)) : 
                marked.parse(content);
        } else {
            // For user messages, just add linebreaks
            messageContent.textContent = content;
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Syntax highlight code blocks if Prism is available
        if (window.Prism) {
            Prism.highlightAllUnder(messageDiv);
        }
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Add to conversation history if it's not already from history
        if (!isHistory) {
            const role = type === 'user-message' ? 'user' : 'assistant';
            conversationHistory.push({
                role: role,
                content: content
            });
        }
    }

    // Handle chat form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;
        
        // Display user message
        addMessage(message, 'user-message');
        
        // Clear input field
        userInput.value = '';
        
        // Get conversation ID from data attribute or create a new one
        const conversationId = chatMessages.dataset.conversationId || generateUUID();
        chatMessages.dataset.conversationId = conversationId;
        
        // Show loading indicators
        showTypingIndicator();
        setButtonLoading(true);
        
        // Send message to backend with conversation history
        fetch('/chat/send_message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                message: message,
                conversation_id: conversationId,
                conversation_history: conversationHistory
            }),
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading indicators
            hideTypingIndicator();
            setButtonLoading(false);
            
            if (data.success) {
                // Display bot response
                addMessage(data.reply, 'bot-message');
                
                // Save conversation ID
                if (data.conversation_id) {
                    chatMessages.dataset.conversationId = data.conversation_id;
                }
                
                // Check if there's form data to populate
                if (data.mineral_data && Object.keys(data.mineral_data).length > 0) {
                    // Save current state before making changes
                    saveFormState();
                    
                    // Update form with new data
                    updateFormFields(data.mineral_data);
                    
                    // Show the revert button
                    revertButton.style.display = 'block';
                }
            } else {
                // Display error
                addMessage('Error: ' + data.error, 'system-message');
            }
        })
        .catch(error => {
            // Hide loading indicators
            hideTypingIndicator();
            setButtonLoading(false);
            
            console.error('Error:', error);
            addMessage('Failed to send message. Please try again.', 'system-message');
        });
    });
    
    // Function to update form fields with new data
    function updateFormFields(data) {
        for (const [key, value] of Object.entries(data)) {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'radio') {
                    // Handle radio buttons
                    const radioButton = document.querySelector(`input[name="${field.name}"][value="${value}"]`);
                    if (radioButton) {
                        radioButton.checked = true;
                    }
                } else if (field.tagName === 'SELECT') {
                    // Handle select elements
                    field.value = value;
                    // Highlight the updated field
                    highlightField(field);
                } else {
                    // Handle normal inputs and textareas
                    field.value = value;
                    // Highlight the updated field
                    highlightField(field);
                }
            }
        }
    }
    
    // Function to highlight a field that has been updated
    function highlightField(field) {
        field.classList.add('updated-field');
        setTimeout(() => {
            field.classList.remove('updated-field');
        }, 3000);
    }
    
    // Function to save current form state
    function saveFormState() {
        const formData = new FormData(mineralForm);
        const formState = {};
        
        for (const [key, value] of formData.entries()) {
            formState[key] = value;
        }
        
        // Handle radio buttons
        const radioButtons = mineralForm.querySelectorAll('input[type="radio"]:checked');
        radioButtons.forEach(radio => {
            formState[radio.name] = radio.value;
        });
        
        // Save to history
        formChangeHistory.push(JSON.parse(JSON.stringify(currentFormState)));
        currentFormState = formState;
    }
    
    // Function to revert to previous form state
    function revertFormChanges() {
        if (formChangeHistory.length === 0) {
            return;
        }
        
        const previousState = formChangeHistory.pop();
        
        // Apply previous state to form
        for (const [key, value] of Object.entries(previousState)) {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'radio') {
                    // Handle radio buttons
                    const radioButton = document.querySelector(`input[name="${field.name}"][value="${value}"]`);
                    if (radioButton) {
                        radioButton.checked = true;
                    }
                } else {
                    // Handle normal inputs, selects, and textareas
                    field.value = value;
                }
            }
        }
        
        currentFormState = previousState;
        
        // Hide revert button if no more history
        if (formChangeHistory.length === 0) {
            revertButton.style.display = 'none';
        }
    }
    
    // Generate a UUID for conversation tracking
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    // Handle mineral form submission
    mineralForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Here you would handle saving the mineral information
        addMessage('Mineral information saved successfully!', 'system-message');
        
        // Clear the form change history after saving
        formChangeHistory = [];
        revertButton.style.display = 'none';
        
        // Save the new base state
        saveFormState();
    });
    
    // Handle form reset
    resetFormButton.addEventListener('click', function() {
        mineralForm.reset();
        addMessage('Form has been reset.', 'system-message');
        
        // Clear the form change history after reset
        formChangeHistory = [];
        revertButton.style.display = 'none';
        
        // Save the new base state
        saveFormState();
    });
    
    // Handle revert button click
    revertButton.addEventListener('click', function() {
        revertFormChanges();
        addMessage('Form changes have been reverted.', 'system-message');
    });
    
    // Track form field changes manually
    const formFields = mineralForm.querySelectorAll('input, select, textarea');
    formFields.forEach(field => {
        field.addEventListener('change', function() {
            revertButton.style.display = 'block';
        });
    });
    
    // Load DOMPurify for HTML sanitization if not present
    if (typeof DOMPurify === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/dompurify/2.3.8/purify.min.js';
        document.head.appendChild(script);
    }
    
    // Load Prism for code highlighting if desired
    if (typeof Prism === 'undefined') {
        // CSS
        const prismCss = document.createElement('link');
        prismCss.rel = 'stylesheet';
        prismCss.href = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/themes/prism.min.css';
        document.head.appendChild(prismCss);
        
        // JS
        const prismJs = document.createElement('script');
        prismJs.src = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/components/prism-core.min.js';
        document.head.appendChild(prismJs);
        
        // Autoloader for language support
        const prismAutoloader = document.createElement('script');
        prismAutoloader.src = 'https://cdnjs.cloudflare.com/ajax/libs/prism/1.25.0/plugins/autoloader/prism-autoloader.min.js';
        document.head.appendChild(prismAutoloader);
    }
    
    // Function to restore conversation from localStorage if available
    function loadConversationFromStorage() {
        const savedHistory = localStorage.getItem('mineralChatHistory');
        const savedConversationId = localStorage.getItem('mineralChatConversationId');
        
        if (savedHistory && savedConversationId) {
            try {
                const historyData = JSON.parse(savedHistory);
                conversationHistory = historyData;
                
                // Display saved messages
                historyData.forEach(item => {
                    const messageType = item.role === 'user' ? 'user-message' : 'bot-message';
                    addMessage(item.content, messageType, true);
                });
                
                // Restore conversation ID
                chatMessages.dataset.conversationId = savedConversationId;
                
                return true;
            } catch (e) {
                console.error('Error restoring conversation:', e);
                // Clear invalid data
                localStorage.removeItem('mineralChatHistory');
                localStorage.removeItem('mineralChatConversationId');
            }
        }
        return false;
    }
    
    // Function to save conversation to localStorage
    function saveConversationToStorage() {
        if (conversationHistory.length > 0) {
            localStorage.setItem('mineralChatHistory', JSON.stringify(conversationHistory));
            localStorage.setItem('mineralChatConversationId', chatMessages.dataset.conversationId);
        }
    }
    
    // Clear conversation history
    function clearConversation() {
        conversationHistory = [];
        chatMessages.innerHTML = '';
        chatMessages.dataset.conversationId = generateUUID();
        
        // Add welcome message
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'system-message';
        
        const welcomeContent = document.createElement('div');
        welcomeContent.className = 'message-content';
        welcomeContent.textContent = 'Welcome to the Mineral Inventory Chat. How can I help you today?';
        
        welcomeDiv.appendChild(welcomeContent);
        chatMessages.appendChild(welcomeDiv);
        
        // Clear storage
        localStorage.removeItem('mineralChatHistory');
        localStorage.removeItem('mineralChatConversationId');
    }
    
    // Add a clear button to the chat header
    const chatHeader = document.querySelector('.chat-header');
    const clearButton = document.createElement('button');
    clearButton.textContent = 'Clear Chat';
    clearButton.className = 'clear-chat-button';
    clearButton.addEventListener('click', clearConversation);
    chatHeader.appendChild(clearButton);
    
    // Load conversation on page load
    loadConversationFromStorage();
    
    // Save conversation before page unload
    window.addEventListener('beforeunload', saveConversationToStorage);
});
