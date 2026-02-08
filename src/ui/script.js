const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// BACKEND_URL should be updated to your Cloud Run service URL
const BACKEND_URL = 'https://sport-expert-chatbot-997402636968.us-central1.run.app';

function addMessage(text, sender) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message');
    msgDiv.classList.add(`${sender}-message`);
    msgDiv.innerText = text;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, 'user');
    userInput.value = '';

    try {
        const response = await fetch(`${BACKEND_URL}/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        });

        const data = await response.json();
        if (data.answer) {
            addMessage(data.answer, 'bot');
        } else {
            addMessage('Error: ' + (data.error || 'Unknown error'), 'system');
        }
    } catch (err) {
        addMessage('Failed to connect to backend: ' + err.message, 'system');
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
