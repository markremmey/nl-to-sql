document.addEventListener('DOMContentLoaded', function(e) {
    e.preventDefault()
    let agentMsgCount = 0
    let userMsgCount = 0
    
    const sendMessage = () => {
        const userQuery = document.getElementById('user-query');
        const message = userQuery.value.trim();

        if (message) {
            displayMessage('User', message, userMsgCount);
            userMsgCount+=1
            userQuery.value = '';
            getAgentResponse(message);
        }
    };

    const displayMessage = (sender, message, msgNo) => {
        const conversation = document.getElementById('conversation');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender, 'msg_' + String(msgNo));
        messageElement.textContent = String(msgNo) + sender + ': ' + message;
        conversation.appendChild(messageElement);
        conversation.scrollTop = conversation.scrollHeight;
    }

    const streamResponse = (sender, message, msgNo) => {
        const conversation = document.getElementById('conversation');
        
        console.log(`Query selector: .message.${sender}.msg_${String(msgNo)}`)
        if (document.querySelector(`.message.${sender}.msg_${String(msgNo)}`)) {
            let messageElement = document.querySelector(`.message.${sender}.msg_${String(msgNo)}`);
            messageElement.textContent += message;
        } else {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', sender, 'msg_' + String(msgNo));
            messageElement.textContent = String(msgNo) + sender + ': ' + message;
            conversation.appendChild(messageElement);
        }
    }

    const getAgentResponse = (message) => {
        console.log(message)
        let errorCount = 0; // Counter for connection errors
        const maxErrors = 3;
        const apiUrl = `http://127.0.0.1:5000/getAgentResponse?message=${encodeURIComponent(message)}`;
        
        console.log(apiUrl)
        const eventSource = new EventSource(apiUrl);  //Web API that establishes a persistent connection to a server

        eventSource.onmessage = function(event) {
            console.log('Message received')
            const data = event.data;
            // Process the JSON data here
            if (data === '[DONE]') {
                console.log('FINISHED')
                eventSource.close();
                agentMsgCount+=1
            } else {
                try {
                    const parsedData = JSON.parse(data);
                    console.log(parsedData)
                    const msg = parsedData.choices // choices 0 content

                    if (parsedData.choices && parsedData.choices.length > 0 && parsedData.choices[0].delta.content) {
                        const content = parsedData.choices[0].delta.content;
                        console.log('Content:', content);
                        streamResponse('Assistant', content, agentMsgCount);
                    } else {
                        console.log('No choices available or choices array is empty');
                    }
                } catch (e) {
                    console.error('Error parsing JSON: ', e);
                }
            }
            
            

        };

        eventSource.onerror = function() {
            errorCount++; // Increment the error counter
    
            // Check if maximum error count is reached
            if (errorCount >= maxErrors) {
                console.error(`Maximum connection errors reached (${maxErrors}). Closing stream.`);
                eventSource.close(); // Close the stream
            }
        };
    }

    // The addEventListener method triggers a function to run on a particular event
    document.getElementById('send-button').addEventListener('click', function(e) {
        e.preventDefault()
        sendMessage()
    });

    document.getElementById('user-query').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault()
            sendMessage();
        }
    });
});
