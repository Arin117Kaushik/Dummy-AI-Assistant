import sqlite3
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "chat.db"

def get_db_connection():
    # Establishes a connection to the SQLite database.
    # row_factory=sqlite3.Row allows accessing columns by name.
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Initializes the database schema if it doesn't exist.
    conn = get_db_connection()
    
    # Users table: Stores user credentials and profile info.
    # 'auth_provider' tracks if they used google, github, or local auth.
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            name TEXT,
            avatar_url TEXT,
            auth_provider TEXT DEFAULT 'local'
        )
    ''')

    # Sessions table: Represents a chat thread.
    # Can belong to a registered user (user_id) or a guest (guest_id).
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            guest_id TEXT,
            title TEXT NOT NULL,
            is_pinned BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Messages table: Stores individual messages within a session.
    # 'role' is either 'user' or 'assistant'.
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    ''')
    conn.commit()
    conn.close()

# --- User Management ---

def register_user(email, password, name, provider='local', avatar_url=None):
    # Creates a new user record.
    # Only hashes password if it exists (social login might not have one).
    password_hash = generate_password_hash(password) if password else None
    user_id = str(uuid.uuid4())
    
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO users (id, email, password_hash, name, auth_provider, avatar_url) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, email, password_hash, name, provider, avatar_url))
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

def authenticate_user(email, password):
    # Verifies email and password for local login.
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_or_create_social_user(email, name, provider, avatar_url):
    """
    Handles social login logic:
    1. Checks if a user with this email already exists.
    2. If yes, logs them in (returns user data).
    3. If no, creates a new account automatically without a password.
    """
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if user:
        # User exists, return their ID
        return dict(user)
    else:
        # Register new social user
        user_id = register_user(email, None, name, provider, avatar_url)
        return {"id": user_id, "name": name, "email": email}

def get_user_by_id(user_id):
    # Fetches user details by ID.
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

# --- Session Management ---

def create_session(user_id=None, guest_id=None, title="New Chat"):
    # Creates a new chat session for a user or guest.
    session_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute('INSERT INTO sessions (id, user_id, guest_id, title) VALUES (?, ?, ?, ?)', 
                 (session_id, user_id, guest_id, title))
    conn.commit()
    conn.close()
    return session_id

def get_sessions(user_id=None, guest_id=None):
    # Retrieves all sessions for a specific user or guest.
    # Ordered by pinned status first, then creation date.
    conn = get_db_connection()
    if user_id:
        query = 'SELECT * FROM sessions WHERE user_id = ? ORDER BY is_pinned DESC, created_at DESC'
        params = (user_id,)
    else:
        query = 'SELECT * FROM sessions WHERE guest_id = ? AND user_id IS NULL ORDER BY is_pinned DESC, created_at DESC'
        params = (guest_id,)
        
    sessions = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(s) for s in sessions]

def update_session_title(session_id, new_title):
    # Updates the display title of a session.
    conn = get_db_connection()
    conn.execute('UPDATE sessions SET title = ? WHERE id = ?', (new_title, session_id))
    conn.commit()
    conn.close()

def toggle_pin_session(session_id, is_pinned):
    # Updates the pinned status of a session.
    conn = get_db_connection()
    conn.execute('UPDATE sessions SET is_pinned = ? WHERE id = ?', (is_pinned, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    # Deletes a session and all its associated messages.
    conn = get_db_connection()
    conn.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()

# --- Message Management ---

def add_message(session_id, role, content):
    # Adds a new message to the database.
    # Also auto-updates the session title if it's the first user message.
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)',
                 (session_id, role, content))
    
    if role == 'user':
        # Check if this is the first message to set a title
        count = conn.execute('SELECT COUNT(*) FROM messages WHERE session_id = ?', (session_id,)).fetchone()[0]
        if count <= 1: 
            # Truncate content for title if too long
            new_title = content[:30] + "..." if len(content) > 30 else content
            conn.execute('UPDATE sessions SET title = ? WHERE id = ?', (new_title, session_id))
    
    conn.commit()
    conn.close()

def get_session_messages(session_id):
    # Retrieves full conversation history for a session.
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC', 
                            (session_id,)).fetchall()
    conn.close()
    return [dict(m) for m in messages]