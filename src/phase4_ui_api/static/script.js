const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const typingIndicator = document.getElementById('typing-indicator');
const welcomeScreen = document.getElementById('welcome-screen');

// Function to add a message to the UI
function addMessage(text, isUser = false) {
    // Hide welcome screen on first message
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;

    const infoDiv = document.createElement('div');
    infoDiv.className = 'message-info';
    infoDiv.innerText = isUser ? 'You' : 'HDFC Assistant';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'bubble';
    
    if (isUser) {
        bubbleDiv.innerText = text;
    } else {
        // Parse the response for Markdown-style links and line breaks
        bubbleDiv.innerHTML = formatResponse(text);
    }

    messageDiv.appendChild(infoDiv);
    messageDiv.appendChild(bubbleDiv);
    
    // Insert before typing indicator
    chatMessages.insertBefore(messageDiv, typingIndicator);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Simple formatter for the RAG response
function formatResponse(text) {
    // 1. Handle newlines
    let html = text.replace(/\n/g, '<br>');
    
    // 2. Handle [Text](URL) citations
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<div class="citation">Source: <a href="$2" target="_blank">$1</a></div>');
    
    // 3. Handle *Last updated* footer
    html = html.replace(/\*(Last updated from sources: [^*]+)\*/g, '<div class="updated-at">$1</div>');
    
    return html;
}

async function handleSendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // Clear input
    userInput.value = '';
    
    // Add user message to UI
    addMessage(query, true);

    // Show typing indicator
    typingIndicator.style.display = 'block';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: query })
        });

        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.style.display = 'none';

        if (response.ok) {
            addMessage(data.response, false);
        } else {
            addMessage(`Error: ${data.detail || 'Something went wrong. Please try again.'}`, false);
        }
    } catch (error) {
        typingIndicator.style.display = 'none';
        addMessage("Connection error: Could not reach the server. Make sure the backend is running.", false);
        console.error('Fetch error:', error);
    }
}

// Event Listeners
sendButton.addEventListener('click', handleSendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

function sendExample(text) {
    userInput.value = text;
    handleSendMessage();
}

// Focus input on load
window.onload = () => userInput.focus();
