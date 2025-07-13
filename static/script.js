const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

// Voice-to-Text Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.lang = 'en-US';
recognition.interimResults = false;

// Handle Speech Result
recognition.onresult = function (event) {
  const transcript = event.results[0][0].transcript;
  input.value = transcript;
  sendMessage();  // Auto-send after speech
};

// Start Listening
function startListening() {
  recognition.start();
}

// Send message to Flask backend
async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    // Add user message to chat box (right side)
    const chatBox = document.getElementById("chat-box");
    const userEntry = document.createElement("div");
    userEntry.className = "chat-entry user";
    userEntry.innerHTML = `
        <div class="bubble user-bubble">
            <p>${message}</p>
        </div>
    `;
    chatBox.appendChild(userEntry);
    chatBox.scrollTop = chatBox.scrollHeight;

    input.value = ""; // clear input

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Add bot message to chat box (left side)
        const botEntry = document.createElement("div");
        botEntry.className = "chat-entry bot";
        botEntry.innerHTML = `
            <div class="bubble bot-bubble">
                <p>${data.response}</p>
                <p class="emotion">🧠 Emotion: <strong>${data.emotions[0][0]}</strong></p>
            </div>
        `;
        chatBox.appendChild(botEntry);
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (error) {
        console.error("Error:", error);
    }
}


// Display messages in chat box
function displayMessage(sender, message) {
  const msg = document.createElement("div");
  msg.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Text-to-Speech
function speak(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US';
  window.speechSynthesis.speak(utterance);
}

// Toggle History Visibility
function toggleHistory() {
  const historyBox = document.getElementById("historyBox");
  const toggleButton = document.getElementById("toggleHistory");
  if (historyBox.style.display === "none") {
    historyBox.style.display = "block";
    toggleButton.innerText = "🙈 Hide History";
  } else {
    historyBox.style.display = "none";
    toggleButton.innerText = "📜 Show History";
  }
}
