# ============================================================
#                    TITAN AI
#             Advanced Python Assistant
# ============================================================

import json
import math
import random
import datetime
import webbrowser
from pathlib import Path

# ------------------------------------------------------------
# SETTINGS
# ------------------------------------------------------------

BOT_NAME = "TITAN"

MEMORY_FILE = Path("titan_memory.json")
HISTORY_FILE = Path("titan_history.json")


# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

def load_data(filename, default):
    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            return default

    return default


def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


memory = load_data(MEMORY_FILE, {})
history = load_data(HISTORY_FILE, [])


# ------------------------------------------------------------
# MEMORY SYSTEM
# ------------------------------------------------------------

def remember(key, value):
    memory[key] = value
    save_data(MEMORY_FILE, memory)


def forget(key):
    if key in memory:
        del memory[key]
        save_data(MEMORY_FILE, memory)
        return f"I forgot {key}."

    return "I don't remember that."


def show_memory():

    if not memory:
        return "My memory is empty."

    output = "Things I remember:\n"

    for key, value in memory.items():
        output += f"• {key}: {value}\n"

    return output


# ------------------------------------------------------------
# CALCULATOR
# ------------------------------------------------------------

def calculate(expression):

    allowed = {
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round
    }

    try:

        expression = expression.replace("^", "**")

        answer = eval(
            expression,
            {"__builtins__": {}},
            allowed
        )

        return f"🧮 Answer: {answer}"

    except:
        return "❌ I couldn't calculate that."


# ------------------------------------------------------------
# DATE & TIME
# ------------------------------------------------------------

def get_time():

    now = datetime.datetime.now()

    return now.strftime(
        "📅 %A, %d %B %Y\n⏰ %I:%M:%S %p"
    )


# ------------------------------------------------------------
# JOKES
# ------------------------------------------------------------

def joke():

    jokes = [
        "Why do programmers hate nature? Too many bugs. 😂",
        "Why was the computer cold? It left its Windows open. 😂",
        "A Python programmer walks into a bar... and finds a bug. 🐍"
    ]

    return random.choice(jokes)


# ------------------------------------------------------------
# HELP
# ------------------------------------------------------------

def help_menu():

    return """
================ TITAN COMMANDS ================

/help
Show this menu.

/time
Show date and time.

/memory
Show saved memory.

/remember name = value
Save something to memory.

/forget name
Delete something from memory.

/calculate 25 * 5
Calculate mathematics.

/random
Generate a random number.

/joke
Tell a joke.

/open google.com
Open a website.

/history
Show recent conversations.

/clear
Clear conversation history.

/quit
Exit TITAN.

==================================================
"""


# ------------------------------------------------------------
# COMMAND PROCESSOR
# ------------------------------------------------------------

def command(message):

    msg = message.strip()

    if msg == "/help":
        return help_menu()

    if msg == "/time":
        return get_time()

    if msg == "/memory":
        return show_memory()

    if msg == "/joke":
        return joke()

    if msg == "/random":
        return f"🎲 Random number: {random.randint(1, 100000)}"

    if msg == "/clear":

        history.clear()
        save_data(HISTORY_FILE, history)

        return "🧹 Conversation history cleared."

    if msg == "/history":

        if not history:
            return "No conversation history."

        result = "\n"

        for item in history[-10:]:

            result += f"You: {item['user']}\n"
            result += f"TITAN: {item['bot']}\n\n"

        return result

    if msg.startswith("/remember "):

        data = msg[len("/remember "):]

        if "=" not in data:
            return "Use: /remember key = value"

        key, value = data.split("=", 1)

        remember(
            key.strip(),
            value.strip()
        )

        return "🧠 Memory saved."

    if msg.startswith("/forget "):

        key = msg[len("/forget "):].strip()

        return forget(key)

    if msg.startswith("/calculate "):

        expression = msg[len("/calculate "):]

        return calculate(expression)

    if msg.startswith("/open "):

        website = msg[len("/open "):].strip()

        if not website.startswith("http"):
            website = "https://" + website

        webbrowser.open(website)

        return f"🌐 Opening {website}"

    if msg == "/quit":
        return "__QUIT__"

    return None


# ------------------------------------------------------------
# BASIC AI BRAIN
# ------------------------------------------------------------

def ai_brain(message):

    msg = message.lower()

    # Greetings
    if msg in ["hi", "hello", "hey", "hii", "helo"]:

        return random.choice([
            "Hey! 👋",
            "Hello! How can I help?",
            "Hey there! 😎",
            "Hello! I'm TITAN."
        ])

    # Name
    if "your name" in msg:
        return "My name is TITAN. 🤖"

    # Creator
    if "who made you" in msg:
        return "I was created using Python."

    # Python
    if "what is python" in msg:

        return (
            "Python is a powerful programming language "
            "used for AI, websites, automation, data science "
            "and many other applications."
        )

    # How are you
    if "how are you" in msg:
        return "I'm running perfectly! 🤖🔥"

    # Thanks
    if "thank" in msg:
        return "You're welcome! 😎"

    # Goodbye
    if msg in ["bye", "goodbye"]:
        return "Goodbye! 👋"

    # Memory
    if "what do you remember" in msg:

        if memory:
            return show_memory()

        return "I don't have anything stored yet."

    # Unknown
    return random.choice([
        "Interesting! Tell me more.",
        "I'm still learning about that.",
        "I don't know that yet.",
        "Can you explain that differently?",
        "That's interesting! 🤖"
    ])


# ------------------------------------------------------------
# MAIN AI LOOP
# ------------------------------------------------------------

def main():

    print()
    print("=" * 60)
    print("                    🤖 TITAN AI")
    print("             ADVANCED PYTHON ASSISTANT")
    print("=" * 60)

    print("Type /help for commands.")
    print("Type /quit to exit.")
    print()

    while True:

        try:

            user = input("YOU  > ").strip()

            if not user:
                continue

            # Check commands first
            response = command(user)

            if response == "__QUIT__":

                print("TITAN > Goodbye! 👋")
                break

            # If command exists
            if response is not None:

                print("\nTITAN >", response)
                print()

                continue

            # AI brain
            response = ai_brain(user)

            print("\nTITAN >", response)
            print()

            # Save conversation
            history.append({
                "user": user,
                "bot": response,
                "time": datetime.datetime.now().isoformat()
            })

            save_data(HISTORY_FILE, history)

        except KeyboardInterrupt:

            print("\n\nTITAN > Goodbye! 👋")
            break

        except Exception as error:

            print("⚠️ Error:", error)


# ------------------------------------------------------------
# START PROGRAM
# ------------------------------------------------------------

if __name__ == "__main__":
    main()
