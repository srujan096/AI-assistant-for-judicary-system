// Add event listeners for the "Send" button and Enter key
document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('chat-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Function to send a message to the backend and display the response
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (message === "") return;

    // Display user message in the chat window
    const chatWindow = document.getElementById('chat-messages');
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.textContent = `You: ${message}`;
    chatWindow.appendChild(userMessage);

    // Clear the input field
    input.value = '';

    // Send the message to the backend
    try {
        const response = await fetch('http://localhost:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        // Check if the response is OK (status code 200-299)
        if (!response.ok) {
            throw new Error(`Network response was not ok: ${response.statusText}`);
        }

        // Parse the JSON response
        const data = await response.json();

        // Display the bot's response in the chat window
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.textContent = `DOJ Assistant: ${data.message}`;
        chatWindow.appendChild(botMessage);
    } catch (error) {
        // Display an error message if something goes wrong
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message bot-message';
        errorMessage.textContent = `DOJ Assistant: Sorry, I am unable to process your request at the moment. (Error: ${error.message})`;
        chatWindow.appendChild(errorMessage);
    }

    // Scroll to the bottom of the chat window
    chatWindow.scrollTop = chatWindow.scrollHeight;
}