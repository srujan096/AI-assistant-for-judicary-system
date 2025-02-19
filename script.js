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

    // Create a container for the bot's streaming response
    const botMessage = document.createElement('div');
    botMessage.className = 'message bot-message';
    botMessage.textContent = 'DOJ Assistant: ';
    chatWindow.appendChild(botMessage);

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

        // Process the streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            // Decode the chunk and append it to the bot's message
            const chunk = decoder.decode(value);
            botMessage.textContent += chunk;

            // Scroll to the bottom of the chat window
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    } catch (error) {
        // Display an error message if something goes wrong
        botMessage.textContent = `DOJ Assistant: Sorry, I am unable to process your request at the moment. (Error: ${error.message})`;
    }

    // Scroll to the bottom of the chat window
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
