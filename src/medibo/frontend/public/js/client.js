
document.addEventListener('DOMContentLoaded', () => {
    const messagesContainer = document.getElementById('messages-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const modules = {
        perception: { bar: document.getElementById('bar-perception'), val: document.getElementById('val-perception'), curr: 20 },
        cognitive: { bar: document.getElementById('bar-cognitive'), val: document.getElementById('val-cognitive'), curr: 10 },
        action: { bar: document.getElementById('bar-action'), val: document.getElementById('val-action'), curr: 5 }
    };

    // Helper: Add message to UI
    function addMessage(text, role, action = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;

        let content = document.createTextNode(text);
        msgDiv.appendChild(content);

        if (action) {
            const actionDiv = document.createElement('div');
            actionDiv.className = 'action-taken';
            actionDiv.innerHTML = `<span>⚙️ System Action:</span> ${action}`;
            msgDiv.appendChild(actionDiv);
        }

        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        // Using settimeout to ensure DOM has updated
        setTimeout(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }, 10);
    }

    // Helper: Simulate module activity
    function setModuleStatus(isThinking) {
        if (isThinking) {
            modules.perception.curr = 90;
            modules.cognitive.curr = 95;
            modules.action.curr = 50;
        } else {
            modules.perception.curr = 20;
            modules.cognitive.curr = 20;
            modules.action.curr = 10;
        }
        updateModulesUI();
    }

    function updateModulesUI() {
        for (const key in modules) {
            const mod = modules[key];
            mod.bar.style.width = `${mod.curr}%`;
            mod.val.innerText = `${mod.curr}%`;
        }
    }

    // Idle animation for modules
    setInterval(() => {
        // Only jitter if not in high thinking mode
        if (modules.perception.curr < 80) {
            for (const key in modules) {
                const mod = modules[key];
                // Random walk
                let change = (Math.random() - 0.5) * 10;
                let newVal = Math.max(10, Math.min(60, mod.curr + change));
                mod.curr = Math.round(newVal);
                mod.bar.style.width = `${mod.curr}%`;
                mod.val.innerText = `${mod.curr}%`;
            }
        }
    }, 1500);


    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // User Message
        addMessage(text, 'user');
        userInput.value = '';
        setModuleStatus(true);

        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerText = 'Thinking...';
        messagesContainer.appendChild(typingDiv);
        scrollToBottom();

        try {
            // Call our Express Proxy
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: 'P001', message: text })
            });

            const data = await response.json();

            // Remove typing indicator
            const ind = document.getElementById('typing-indicator');
            if (ind) ind.remove();

            addMessage(data.response, 'bot', data.action_taken);

        } catch (error) {
            console.error(error);
            const ind = document.getElementById('typing-indicator');
            if (ind) ind.remove();
            addMessage("Error: Could not connect to MediBo Brain.", 'bot');
        } finally {
            setModuleStatus(false);
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
