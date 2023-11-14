document.addEventListener('DOMContentLoaded', function() {
    const sendMessage = () => {
        const userQuery = document.getElementById('user-query');
        const message = userQuery.value.trim();

        if (message) {
            displayMessage('user', message);
            userQuery.value = '';
            getAgentResponse(message);
        }
    };

    const displayMessage = (sender, message) => {
        const conversation = document.getElementById('conversation');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        messageElement.textContent = message;
        conversation.appendChild(messageElement);
        conversation.scrollTop = conversation.scrollHeight;
    }

    // The addEventListener method triggers a function to run on a particular event
    document.getElementById('send-button').addEventListener('click', sendMessage);

    document.getElementById('user-query').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
