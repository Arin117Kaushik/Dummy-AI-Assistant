from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import database
from ai_engine import GeminiHandler
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) # Required for session management
CORS(app)

# Initialize DB and AI
database.init_db()
ai_handler = GeminiHandler()

# Middleware to check auth
def is_logged_in():
    return 'user_id' in session

@app.route('/')
def index():
    return render_template('index.html')

# --- Auth Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    user_id = database.register_user(data['email'], data['password'], data.get('name'))
    if user_id:
        session['user_id'] = user_id
        return jsonify({"success": True, "user_id": user_id})
    return jsonify({"error": "Email already registered"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = database.authenticate_user(data['email'], data['password'])
    if user:
        session['user_id'] = user['id']
        return jsonify({"success": True, "user": user})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True})

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    if is_logged_in():
        return jsonify({"authenticated": True, "user_id": session['user_id']})
    return jsonify({"authenticated": False})

# --- Session Routes ---
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    if not is_logged_in(): return jsonify([]), 401
    sessions = database.get_user_sessions(session['user_id'])
    return jsonify(sessions)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    if not is_logged_in(): return jsonify({"error": "Unauthorized"}), 401
    session_id = database.create_session(session['user_id'])
    return jsonify({"session_id": session_id})

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    if not is_logged_in(): return jsonify({"error": "Unauthorized"}), 401
    database.delete_session(session_id)
    return jsonify({"success": True})

@app.route('/api/sessions/<session_id>/rename', methods=['POST'])
def rename_session(session_id):
    if not is_logged_in(): return jsonify({"error": "Unauthorized"}), 401
    new_title = request.json.get('title')
    database.update_session_title(session_id, new_title)
    return jsonify({"success": True})

@app.route('/api/sessions/<session_id>/pin', methods=['POST'])
def pin_session(session_id):
    if not is_logged_in(): return jsonify({"error": "Unauthorized"}), 401
    is_pinned = request.json.get('is_pinned')
    database.toggle_pin_session(session_id, is_pinned)
    return jsonify({"success": True})

# --- Chat Routes ---
@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    if not is_logged_in(): return jsonify([]), 401
    messages = database.get_session_messages(session_id)
    return jsonify(messages)

@app.route('/api/chat', methods=['POST'])
def chat():
    if not is_logged_in(): return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')

    if not session_id or not user_message:
        return jsonify({"error": "Missing data"}), 400

    # 1. Get Context
    current_history = database.get_session_messages(session_id)
    
    # 2. Save User Message
    database.add_message(session_id, "user", user_message)

    # 3. Generate Response
    ai_response = ai_handler.generate_response(current_history, user_message)

    # 4. Save AI Response
    database.add_message(session_id, "assistant", ai_response)

    return jsonify({
        "response": ai_response
    })

if __name__ == '__main__':
    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True, port=5000)