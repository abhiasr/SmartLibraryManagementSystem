const chatbotContainer = document.querySelector('.chatbot-container');
const chatbotBody = document.getElementById('chatbot-body');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function toggleChatbot() {
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex';
    } else {
        chatbotContainer.style.display = 'none';
    }
}

function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    // Display user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.classList.add('message', 'user-message');
    userMessageDiv.textContent = message;
    chatbotBody.appendChild(userMessageDiv);
    userInput.value = '';
    chatbotBody.scrollTop = chatbotBody.scrollHeight;

    // Send message to server and get bot response
    fetch('/get_chatbot_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'message': message })
    })
    .then(response => response.json())
    .then(data => {
        const botMessageDiv = document.createElement('div');
        botMessageDiv.classList.add('message', 'bot-message');
        botMessageDiv.textContent = data.response;
        chatbotBody.appendChild(botMessageDiv);
        chatbotBody.scrollTop = chatbotBody.scrollHeight;
    })
    .catch(error => {
        console.error('Error fetching chatbot response:', error);
        const errorMessageDiv = document.createElement('div');
        errorMessageDiv.classList.add('message', 'bot-message');
        errorMessageDiv.textContent = 'Sorry, there was an error. Please try again.';
        chatbotBody.appendChild(errorMessageDiv);
    });
}

// Event listeners for sending message
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
