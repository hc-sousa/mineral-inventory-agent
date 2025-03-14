document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const mineralForm = document.getElementById('mineral-form');
    const resetFormButton = document.getElementById('reset-form');

    // Function to add a message to the chat interface
    function addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = type;
        
        const messagePara = document.createElement('p');
        messagePara.textContent = content;
        
        messageDiv.appendChild(messagePara);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to the bottom of the chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
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
        
        // Send message to backend
        fetch('/chat/send_message/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Display bot response
                addMessage(data.reply, 'bot-message');
                
                // Check if there's form data to populate
                if (data.mineral_data) {
                    populateFormData(data.mineral_data);
                }
            } else {
                // Display error
                addMessage('Error: ' + data.error, 'system-message');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Failed to send message. Please try again.', 'system-message');
        });
    });
    
    // Function to populate form fields from AI response
    function populateFormData(data) {
        // Loop through all properties in data and set form field values
        for (const [key, value] of Object.entries(data)) {
            const field = document.getElementById(key);
            if (field) {
                if (field.type === 'radio') {
                    // Handle radio buttons
                    document.querySelector(`input[name="${field.name}"][value="${value}"]`).checked = true;
                } else {
                    field.value = value;
                }
            }
        }
    }
    
    // Handle mineral form submission
    mineralForm.addEventListener('submit', function(e) {
        e.preventDefault();
        // Here you would handle saving the mineral information
        addMessage('Mineral information saved successfully!', 'system-message');
    });
    
    // Handle form reset
    resetFormButton.addEventListener('click', function() {
        mineralForm.reset();
        addMessage('Form has been reset.', 'system-message');
    });
});
