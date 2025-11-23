from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
import database
from ai_engine import GeminiHandler
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- HOTFIX FOR LOCAL OAUTH ---
# This allows OAuth to work over HTTP (not HTTPS) for localhost
# Only use this in development!
if os.getenv('OAUTHLIB_INSECURE_TRANSPORT'):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = os.getenv('OAUTHLIB_INSECURE_TRANSPORT')
# -----------------------------

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize DB and AI
database.init_db()
ai_handler = GeminiHandler()

# --- OAuth Configuration ---
oauth = OAuth(app)

# 1. Google Configuration
# Ensure "Authorized redirect URIs" in Google Console is EXACTLY: 
# http://127.0.0.1:5000/auth/callback/google
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# 2. GitHub Configuration
# Ensure "Authorization callback URL" in GitHub Settings is EXACTLY:
# http://127.0.0.1:5000/auth/callback/github
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Helper: Get Current User Identity
def get_identity():
    if 'user_id' in session:
        return {'type': 'user', 'id': session['user_id']}
    guest_id = request.headers.get('X-Guest-ID')
    if guest_id:
        return {'type': 'guest', 'id': guest_id}
    return None

@app.route('/')
def index():
    return render_template('index.html')

# --- Social Login Routes (Fixed for Redirect Mismatch) ---

@app.route('/login/google')
def login_google():
    # Force the redirect URI to be 127.0.0.1 to match Google Console
    redirect_uri = 'http://127.0.0.1:5000/auth/callback/google'
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/callback/google')
def authorize_google():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    if user_info:
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        user = database.get_or_create_social_user(email, name, 'google', picture)
        session['user_id'] = user['id']
        
    return redirect('/')

@app.route('/login/github')
def login_github():
    # Force the redirect URI to be 127.0.0.1 to match GitHub Settings
    redirect_uri = 'http://127.0.0.1:5000/auth/callback/github'
    return oauth.github.authorize_redirect(redirect_uri)

@app.route('/auth/callback/github')
def authorize_github():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get('user', token=token)
    profile = resp.json()
    
    email = profile.get('email')
    if not email:
        email_resp = oauth.github.get('user/emails', token=token)
        emails = email_resp.json()
        for e in emails:
            if e['primary']:
                email = e['email']
                break
                
    name = profile.get('name') or profile.get('login')
    avatar = profile.get('avatar_url')
    
    user = database.get_or_create_social_user(email, name, 'github', avatar)
    session['user_id'] = user['id']
    
    return redirect('/')

# --- Standard Auth Routes ---

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
    if 'user_id' in session:
        user = database.get_user_by_id(session['user_id'])
        if user:
            return jsonify({
                "authenticated": True, 
                "user_id": session['user_id'],
                "name": user['name'],
                "avatar": user['avatar_url']
            })
    return jsonify({"authenticated": False})

# --- Session & Chat Routes ---
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    identity = get_identity()
    if not identity: return jsonify([])
    
    if identity['type'] == 'user':
        sessions = database.get_sessions(user_id=identity['id'])
    else:
        sessions = database.get_sessions(guest_id=identity['id'])
    return jsonify(sessions)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    identity = get_identity()
    if not identity: return jsonify({"error": "No identity"}), 401
    
    if identity['type'] == 'user':
        session_id = database.create_session(user_id=identity['id'])
    else:
        session_id = database.create_session(guest_id=identity['id'])
    return jsonify({"session_id": session_id})

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    database.delete_session(session_id)
    return jsonify({"success": True})

@app.route('/api/sessions/<session_id>/rename', methods=['POST'])
def rename_session(session_id):
    database.update_session_title(session_id, request.json.get('title'))
    return jsonify({"success": True})

@app.route('/api/sessions/<session_id>/pin', methods=['POST'])
def pin_session(session_id):
    database.toggle_pin_session(session_id, request.json.get('is_pinned'))
    return jsonify({"success": True})

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    messages = database.get_session_messages(session_id)
    return jsonify(messages)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    
    if not session_id or not user_message:
        return jsonify({"error": "Missing data"}), 400

    current_history = database.get_session_messages(session_id)
    database.add_message(session_id, "user", user_message)
    ai_response = ai_handler.generate_response(current_history, user_message)
    database.add_message(session_id, "assistant", ai_response)

    return jsonify({"response": ai_response})

if __name__ == '__main__':
    print("🚀 Server running at http://127.0.0.1:5000")
    # Force host to 0.0.0.0 to allow external connections if needed, but primarily for consistency
    app.run(debug=True, port=5000)