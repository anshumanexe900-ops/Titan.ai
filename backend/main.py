# ============================================================
#                         TITAN AI
#              Advanced Python Web Assistant
# ============================================================

import ast
import datetime
import json
import math
import os
import random
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, request
from flask_cors import CORS


# ============================================================
# SETTINGS
# ============================================================

BOT_NAME = "TITAN"

MEMORY_FILE = Path("titan_memory.json")
HISTORY_FILE = Path("titan_history.json")


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

# Allows your frontend to communicate with this backend.
# We can restrict this to your frontend domain later.
CORS(app)


# ============================================================
# DATABASE
# ============================================================

def load_data(filename, default):
    """Load JSON data safely."""

    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as file:
                return json.load(file)

        except (json.JSONDecodeError, OSError):
            return default

    return default


def save_data(filename, data):
    """Save JSON data safely."""

    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError:
        pass


memory = load_data(MEMORY_FILE, {})
history = load_data(HISTORY_FILE, [])


# ============================================================
# MEMORY SYSTEM
# ============================================================

def remember(key, value):
    key = key.strip()
    value = value.strip()

    if not key:
        return "Please provide a memory name."

    memory[key] = value
    save_data(MEMORY_FILE, memory)

    return f"🧠 I'll remember {key}."


def forget(key):
    key = key.strip()

    if key in memory:
        del memory[key]
        save_data(MEMORY_FILE, memory)

        return f"I forgot {key}."

    return "I don't remember that."


def show_memory():

    if not memory:
        return "My memory is empty."

    output = "🧠 Things I remember:\n\n"

    for key, value in memory.items():
        output += f"• {key}: {value}\n"

    return output


# ============================================================
# SAFE CALCULATOR
# ============================================================

ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "abs": abs,
    "round": round,
}

ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


def safe_calculate(expression):
    """
    Safely calculate mathematical expressions.

    Only basic arithmetic and approved math functions
    are allowed.
    """

    expression = expression.replace("^", "**").strip()

    if not expression:
        return "❌ Please provide a calculation."

    try:
        tree = ast.parse(expression, mode="eval")
        result = evaluate_node(tree.body)

        return f"🧮 Answer: {result}"

    except Exception:
        return "❌ I couldn't calculate that."


def evaluate_node(node):

    # Numbers
    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Invalid value")

    # Arithmetic
    if isinstance(node, ast.BinOp):

        left = evaluate_node(node.left)
        right = evaluate_node(node.right)

        if isinstance(node.op, ast.Add):
            return left + right

        if isinstance(node.op, ast.Sub):
            return left - right

        if isinstance(node.op, ast.Mult):
            return left * right

        if isinstance(node.op, ast.Div):
            return left / right

        if isinstance(node.op, ast.FloorDiv):
            return left // right

        if isinstance(node.op, ast.Mod):
            return left % right

        if isinstance(node.op, ast.Pow):

            # Prevent extremely large calculations.
            if abs(right) > 100:
                raise ValueError("Power too large")

            return left ** right

        raise ValueError("Operator not allowed")

    # Positive / negative numbers
    if isinstance(node, ast.UnaryOp):

        value = evaluate_node(node.operand)

        if isinstance(node.op, ast.USub):
            return -value

        if isinstance(node.op, ast.UAdd):
            return +value

        raise ValueError("Operator not allowed")

    # Functions and constants
    if isinstance(node, ast.Name):

        if node.id in ALLOWED_CONSTANTS:
            return ALLOWED_CONSTANTS[node.id]

        raise ValueError("Name not allowed")

    if isinstance(node, ast.Call):

        if not isinstance(node.func, ast.Name):
            raise ValueError("Function not allowed")

        function_name = node.func.id

        if function_name not in ALLOWED_FUNCTIONS:
            raise ValueError("Function not allowed")

        arguments = [
            evaluate_node(argument)
            for argument in node.args
        ]

        return ALLOWED_FUNCTIONS[function_name](*arguments)

    raise ValueError("Expression not allowed")


# ============================================================
# DATE & TIME
# ============================================================

def get_time():

    now = datetime.datetime.now()

    return now.strftime(
        "📅 %A, %d %B %Y\n"
        "⏰ %I:%M:%S %p"
    )


# ============================================================
# JOKES
# ============================================================

def joke():

    jokes = [
        "Why do programmers hate nature? Too many bugs. 😂",
        "Why was the computer cold? It left its Windows open. 😂",
        "A Python programmer walks into a bar... and finds a bug. 🐍",
        "Why did the developer go broke? Too many cache problems. 😂",
        "Why do programmers prefer dark mode? Because light attracts bugs. 🐛"
    ]

    return random.choice(jokes)


# ============================================================
# RANDOM NUMBER
# ============================================================

def random_number():

    return f"🎲 Random number: {random.randint(1, 100000)}"


# ============================================================
# HELP MENU
# ============================================================

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
Create a website link.

/history
Show recent conversations.

/clear
Clear conversation history.

/quit
Exit TITAN.

==================================================
"""


# ============================================================
# COMMAND PROCESSOR
# ============================================================

def command(message):

    msg = message.strip()

    # Help
    if msg.lower() == "/help":
        return help_menu()

    # Time
    if msg.lower() == "/time":
        return get_time()

    # Memory
    if msg.lower() == "/memory":
        return show_memory()

    # Joke
    if msg.lower() == "/joke":
        return joke()

    # Random
    if msg.lower() == "/random":
        return random_number()

    # Clear history
    if msg.lower() == "/clear":

        history.clear()
        save_data(HISTORY_FILE, history)

        return "🧹 Conversation history cleared."

    # History
    if msg.lower() == "/history":

        if not history:
            return "No conversation history."

        result = "📜 Recent conversations:\n\n"

        for item in history[-10:]:

            result += f"You: {item['user']}\n"
            result += f"TITAN: {item['bot']}\n"
            result += f"Time: {item['time']}\n\n"

        return result

    # Remember
    if msg.lower().startswith("/remember "):

        data = msg[len("/remember "):]

        if "=" not in data:
            return "Use: /remember key = value"

        key, value = data.split("=", 1)

        return remember(
            key.strip(),
            value.strip()
        )

    # Forget
    if msg.lower().startswith("/forget "):

        key = msg[len("/forget "):].strip()

        return forget(key)

    # Calculator
    if msg.lower().startswith("/calculate "):

        expression = msg[len("/calculate "):]

        return safe_calculate(expression)

    # Open website
    if msg.lower().startswith("/open "):

        website = msg[len("/open "):].strip()

        if not website:
            return "Please provide a website."

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        parsed = urlparse(website)

        if not parsed.netloc:
            return "❌ Invalid website."

        # A web server cannot open a browser on the user's phone.
        # Return the link instead.
        return f"🌐 Open this website: {website}"

    # Quit
    if msg.lower() == "/quit":

        return "__QUIT__"

    return None


# ============================================================
# BASIC AI BRAIN
# ============================================================

def ai_brain(message):

    msg = message.lower().strip()

    # Greetings
    if msg in [
        "hi",
        "hello",
        "hey",
        "hii",
        "helo",
        "hey titan",
        "hi titan"
    ]:

        return random.choice([
            "Hey! 👋",
            "Hello! How can I help?",
            "Hey there! 😎",
            "Hello! I'm TITAN. 🤖",
            "Hey! TITAN is online. 🔥"
        ])

    # Name
    if "your name" in msg or "who are you" in msg:

        return "My name is TITAN AI. 🤖"

    # Creator
    if "who made you" in msg or "who created you" in msg:

        return "I was created using Python. 🚀"

    # Python
    if "what is python" in msg:

        return (
            "Python is a powerful programming language used "
            "for AI, websites, automation, data science, "
            "games and many other applications."
        )

    # AI
    if "what is ai" in msg or "what is artificial intelligence" in msg:

        return (
            "AI, or artificial intelligence, is technology "
            "that allows computers to perform tasks that "
            "normally require human-like intelligence."
        )

    # How are you
    if "how are you" in msg:

        return "I'm running perfectly! 🤖🔥"

    # Thanks
    if (
        "thank you" in msg
        or "thanks" in msg
        or "thank" in msg
    ):

        return "You're welcome! 😎"

    # Goodbye
    if msg in ["bye", "goodbye", "see you"]:

        return "Goodbye! 👋"

    # Memory
    if (
        "what do you remember" in msg
        or "show my memory" in msg
    ):

        return show_memory()

    # Time
    if "what time is it" in msg:

        return get_time()

    # Joke
    if "tell me a joke" in msg:

        return joke()

    # Unknown
    return random.choice([
        "Interesting! Tell me more. 🤖",
        "I'm still learning about that.",
        "I don't know that yet.",
        "Can you explain that differently?",
        "That's interesting! Tell me more.",
        "I'm working on becoming smarter. 🧠"
    ])


# ============================================================
# SAVE CHAT HISTORY
# ============================================================

def save_conversation(user_message, bot_response):

    history.append({
        "user": user_message,
        "bot": bot_response,
        "time": datetime.datetime.now().isoformat()
    })

    # Keep the file from growing forever.
    if len(history) > 500:
        del history[:-500]

    save_data(HISTORY_FILE, history)


# ============================================================
# WEB API — HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "name": BOT_NAME,
        "status": "online",
        "message": "🤖 TITAN AI is online!",
        "version": "1.0"
    })


# ============================================================
# WEB API — HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy",
        "bot": BOT_NAME
    })


# ============================================================
# WEB API — CHAT
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json(silent=True) or {}

        message = str(
            data.get("message", "")
        ).strip()

        if not message:

            return jsonify({
                "error": "Message cannot be empty."
            }), 400

        # Process command first.
        response = command(message)

        # Normal AI response.
        if response is None:
            response = ai_brain(message)

        # Quit command shouldn't stop the web server.
        if response == "__QUIT__":
            response = "TITAN stays online on the web! 🤖"

        save_conversation(
            message,
            response
        )

        return jsonify({
            "reply": response,
            "bot": BOT_NAME
        })

    except Exception:

        return jsonify({
            "reply": "⚠️ Something went wrong. Please try again."
        }), 500


# ============================================================
# WEB API — MEMORY
# ============================================================

@app.route("/memory", methods=["GET"])
def memory_api():

    return jsonify({
        "memory": memory
    })


# ============================================================
# WEB API — HISTORY
# ============================================================

@app.route("/history", methods=["GET"])
def history_api():

    return jsonify({
        "history": history[-50:]
    })


# ============================================================
# WEB API — CLEAR HISTORY
# ============================================================

@app.route("/history/clear", methods=["POST"])
def clear_history():

    history.clear()

    save_data(
        HISTORY_FILE,
        history
    )

    return jsonify({
        "message": "Conversation history cleared."
    })


# ============================================================
# LOCAL TERMINAL MODE
# ============================================================

def terminal_mode():

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

            response = command(user)

            if response == "__QUIT__":

                print("TITAN > Goodbye! 👋")
                break

            if response is not None:

                print("\nTITAN >", response)
                print()

                continue

            response = ai_brain(user)

            print("\nTITAN >", response)
            print()

            save_conversation(
                user,
                response
            )

        except KeyboardInterrupt:

            print("\n\nTITAN > Goodbye! 👋")
            break

        except Exception as error:

            print("⚠️ Error:", error)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    # When running normally with:
    # python main.py
    # use terminal mode.

    terminal_mode()
