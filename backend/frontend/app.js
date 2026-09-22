const API_URL = "https://titan-ai-dsnt.onrender.com";

async function sendMessage() {
    const input = document.getElementById("message");
    const chat = document.getElementById("chat");

    const text = input.value.trim();

    if (!text) return;

    // User message
    const userMessage = document.createElement("div");
    userMessage.className = "user";
    userMessage.textContent = text;
    chat.appendChild(userMessage);

    input.value = "";
    chat.scrollTop = chat.scrollHeight;

    // Thinking message
    const thinking = document.createElement("div");
    thinking.className = "bot";
    thinking.textContent = "TITAN is thinking... 🤖";
    chat.appendChild(thinking);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text
            })
        });

        const data = await response.json();

        thinking.textContent = data.reply || "I didn't understand that.";

    } catch (error) {
        thinking.textContent =
            "⚠️ I couldn't connect to TITAN's server.";
    }

    chat.scrollTop = chat.scrollHeight;
}


// Press Enter to send
document.getElementById("message").addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
