from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import logging
from Ai import process_message  # Ensure this import is correct

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Path to memory file
MEMORY_FILE = "foxie_memory.json"

# Load memory from file
def load_memory():
    try:
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning("Memory file not found or invalid, initializing fresh memory.")
        return {"blocked_words": [], "instructions": [], "remembered_users": []}

# Save memory to file
def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)

# Initialize memory
memory = load_memory()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('send_message')
def handle_send_message_event(data):
    user_message = data['message']
    response = process_message("User", user_message)  # Process the message
    emit('receive_message', {'user': 'AI', 'message': response}, broadcast=True)

# API to get instructions
@app.route('/api/instructions', methods=['GET'])
def get_instructions():
    return jsonify({"instructions": memory.get("instructions", [])})

# API to set instructions
@app.route('/api/instructions', methods=['POST'])
def set_instructions():
    instructions = request.json.get('instructions', [])
    memory['instructions'] = instructions
    save_memory(memory)
    return jsonify({"status": "success", "instructions": instructions})

# API to get memory
@app.route('/api/memory', methods=['GET'])
def get_memory():
    return jsonify(memory)

# API to update memory
@app.route('/api/memory', methods=['POST'])
def update_memory():
    new_memory = request.json
    memory.update(new_memory)
    save_memory(memory)
    return jsonify({"status": "success", "memory": memory})

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    socketio.run(app, debug=True, use_reloader=False)

