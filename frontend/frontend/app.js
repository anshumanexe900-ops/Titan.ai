async function sendMessage() {

    const input = document.getElementById("message");
    const chat = document.getElementById("chat");

    const text = input.value.trim();

    if (!text) return;

    chat.innerHTML += `
        <div class="user">${text}</div>
    `;

    input.value = "";

    try {

        const response = await fetch(
            "YOUR_BACKEND_URL/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    message: text
                })
            }
        );

        const data = await response.json();

        chat.innerHTML += `
            <div class="bot">${data.reply}</div>
        `;

    } catch {

        chat.innerHTML += `
            <div class="bot">
                ⚠️ Server connection failed.
            </div>
        `;
    }
}
