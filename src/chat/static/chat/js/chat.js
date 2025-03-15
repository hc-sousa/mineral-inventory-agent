document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const mineralForm = document.getElementById('mineral-form');
    const resetFormButton = document.getElementById('reset-form');
    const sendButton = document.getElementById('send-button');
    const micButton = document.getElementById('mic-button');
    
    // Track conversation history
    let conversationHistory = [];
    
    // Track form changes for revert functionality
    let formChangeHistory = [];
    let currentFormState = {};
    
    // Speech recognition variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
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
        console.log("Updating form with data:", data);
        
        // Special handling for generic price field
        if (data.price !== undefined) {
            // If there's a generic "price" field, map it to the appropriate price field
            const pricingType = data.pricing_type || "fixed";
            
            if (pricingType === "auction") {
                // For auctions, use as starting price
                const startingPrice = document.getElementById('starting_price');
                if (startingPrice) {
                    startingPrice.value = data.price;
                    highlightField(startingPrice);
                    console.log(`Mapped general price ${data.price} to starting_price for auction`);
                }
            } else {
                // For fixed price, use as buy_now_price
                const buyNowPrice = document.getElementById('buy_now_price');
                if (buyNowPrice) {
                    buyNowPrice.value = data.price;
                    highlightField(buyNowPrice);
                    console.log(`Mapped general price ${data.price} to buy_now_price for fixed price`);
                }
            }
        }
        
        // Handle dimensions if they're in a non-standard format
        if (data.dimensions) {
            const dimensionsMatch = data.dimensions.match(/(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)/i);
            if (dimensionsMatch) {
                const [, height, width, depth] = dimensionsMatch;
                
                const heightField = document.getElementById('height');
                const widthField = document.getElementById('width');
                const depthField = document.getElementById('depth');
                
                if (heightField && height) {
                    heightField.value = parseFloat(height);
                    highlightField(heightField);
                }
                
                if (widthField && width) {
                    widthField.value = parseFloat(width);
                    highlightField(widthField);
                }
                
                if (depthField && depth) {
                    depthField.value = parseFloat(depth);
                    highlightField(depthField);
                }
                
                console.log(`Parsed dimensions ${data.dimensions} into H:${height}, W:${width}, D:${depth}`);
            }
        }
        
        // Process all other fields normally
        for (const [key, value] of Object.entries(data)) {
            // Skip the price field as we've already handled it specially
            if (key === 'price' || key === 'dimensions') continue;
            
            const field = document.getElementById(key);
            console.log(`Processing field: ${key}, value:`, value, "Field element:", field);
            
            if (field) {
                if (field.type === 'radio') {
                    // Handle radio buttons
                    const radioButton = document.querySelector(`input[name="${field.name}"][value="${value}"]`);
                    if (radioButton) {
                        radioButton.checked = true;
                        highlightField(radioButton);
                        console.log(`Set radio button ${field.name} to ${value}`);
                    }
                } else if (field.tagName === 'SELECT') {
                    // Handle select elements
                    field.value = value;
                    highlightField(field);
                    console.log(`Set select field ${key} to ${value}`);
                } else if (Array.isArray(value)) {
                    // Handle array values (like minerals)
                    field.value = value.join(', ');
                    highlightField(field);
                    console.log(`Set array field ${key} to ${field.value}`);
                } else {
                    // Handle normal inputs and textareas, including null values
                    field.value = value !== null ? value : '';
                    highlightField(field);
                    console.log(`Set field ${key} to ${field.value}`);
                }
            } else {
                // Special handling for specific fields that might be named differently
                if (key === 'buy_now_price' || key === 'starting_price' || key === 'reserve_price') {
                    // Try with and without underscore
                    const alternateKey = key.replace('_', '');
                    const alternateField = document.getElementById(alternateKey);
                    if (alternateField) {
                        alternateField.value = value !== null ? value : '';
                        highlightField(alternateField);
                        console.log(`Set alternate field ${alternateKey} to ${alternateField.value}`);
                    } else {
                        console.log(`Could not find field for ${key} or ${alternateKey}`);
                    }
                } else {
                    console.log(`Field not found: ${key}`);
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
    
    // Speech-to-text functionality
    micButton.addEventListener('click', toggleRecording);
    
    function toggleRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }
    
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Update UI to show recording state
            isRecording = true;
            micButton.classList.add('recording');
            micButton.querySelector('.fa-microphone').style.display = 'none';
            micButton.querySelector('.fa-microphone-slash').style.display = 'inline';
            
            // Create media recorder with WAV or compatible format
            const mimeType = getSupportedMimeType();
            console.log(`Using MIME type: ${mimeType}`);
            
            mediaRecorder = new MediaRecorder(stream, { 
                mimeType: mimeType,
                audioBitsPerSecond: 128000 
            });
            audioChunks = [];
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', processRecording);
            
            // Start recording with smaller timeslice for more frequent dataavailable events
            mediaRecorder.start(100);
            
            // Add a system message to indicate recording
            addMessage('Recording... Click the microphone button again to stop.', 'system-message');
            
        } catch (error) {
            console.error('Error accessing microphone:', error);
            addMessage('Unable to access microphone. Please check permissions and try again.', 'system-message');
        }
    }
    
    // Function to get supported audio MIME type
    function getSupportedMimeType() {
        const types = [
            'audio/wav',
            'audio/webm',
            'audio/webm;codecs=opus',
            'audio/ogg;codecs=opus',
            'audio/mp4',
            'audio/mpeg'
        ];
        
        for (let type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        // Default to standard WebM audio
        return 'audio/webm';
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            // Update UI
            isRecording = false;
            micButton.classList.remove('recording');
            micButton.querySelector('.fa-microphone').style.display = 'inline';
            micButton.querySelector('.fa-microphone-slash').style.display = 'none';
            
            // Stop recording
            mediaRecorder.stop();
            
            // Add system message
            addMessage('Processing speech...', 'system-message');
        }
    }
    
    function processRecording() {
        // Get the mime type that was used for recording
        const mimeType = mediaRecorder.mimeType;
        console.log(`Processing recording with MIME type: ${mimeType}`);
        
        // Create audio blob from chunks with proper MIME type
        const audioBlob = new Blob(audioChunks, { type: mimeType });
        
        // Create a more descriptive filename with the correct extension
        const extension = mimeType.includes('webm') ? 'webm' : 
                          mimeType.includes('ogg') ? 'ogg' : 
                          mimeType.includes('mp4') ? 'mp4' : 
                          mimeType.includes('mp3') ? 'mp3' : 'wav';
        
        // Create form data to send to server
        const formData = new FormData();
        formData.append('audio', audioBlob, `recording.${extension}`);
        
        // Show loading state
        setButtonLoading(true);
        
        // Get CSRF token from cookie
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        const csrftoken = getCookie('csrftoken');
        
        // Send to speech-to-text API
        fetch('/api/speech-to-text/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Speech recognition failed');
            }
            return response.json();
        })
        .then(data => {
            setButtonLoading(false);
            
            if (data.text) {
                // Add the transcribed text to the input field
                userInput.value = data.text;
                userInput.focus();
                
                // Remove processing message
                const messages = chatMessages.getElementsByClassName('system-message');
                if (messages.length > 0) {
                    messages[messages.length - 1].remove();
                }
            } else {
                throw new Error('No text returned from speech recognition');
            }
        })
        .catch(error => {
            setButtonLoading(false);
            console.error('Speech recognition error:', error);
            addMessage('Failed to transcribe speech. Please try again or type your message.', 'system-message');
        });
    }
});
