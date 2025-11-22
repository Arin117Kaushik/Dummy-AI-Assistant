import sqlite3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "chat.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables for users, sessions and messages."""
    conn = get_db_connection()
    
    # Users Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT
        )
    ''')

    # Sessions Table (Updated with user_id and is_pinned)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            is_pinned BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Messages Table
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
def register_user(email, password, name):
    password_hash = generate_password_hash(password)
    user_id = str(uuid.uuid4())
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (id, email, password_hash, name) VALUES (?, ?, ?, ?)',
                     (user_id, email, password_hash, name))
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Email already exists

def authenticate_user(email, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

# --- Session Management ---
def create_session(user_id, title="New Chat"):
    session_id = str(uuid.uuid4())
    conn = get_db_connection()
    conn.execute('INSERT INTO sessions (id, user_id, title) VALUES (?, ?, ?)', 
                 (session_id, user_id, title))
    conn.commit()
    conn.close()
    return session_id

def get_user_sessions(user_id):
    """Retrieve all sessions for a user, pinned first, then by date."""
    conn = get_db_connection()
    sessions = conn.execute('''
        SELECT * FROM sessions 
        WHERE user_id = ? 
        ORDER BY is_pinned DESC, created_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(s) for s in sessions]

def update_session_title(session_id, new_title):
    conn = get_db_connection()
    conn.execute('UPDATE sessions SET title = ? WHERE id = ?', (new_title, session_id))
    conn.commit()
    conn.close()

def toggle_pin_session(session_id, is_pinned):
    conn = get_db_connection()
    conn.execute('UPDATE sessions SET is_pinned = ? WHERE id = ?', (is_pinned, session_id))
    conn.commit()
    conn.close()

def delete_session(session_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    conn.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()

# --- Message Management ---
def add_message(session_id, role, content):
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)',
                 (session_id, role, content))
    
    # Auto-title logic for first user message
    if role == 'user':
        count = conn.execute('SELECT COUNT(*) FROM messages WHERE session_id = ?', (session_id,)).fetchone()[0]
        if count <= 1: 
            # Keep title short
            new_title = content[:30] + "..." if len(content) > 30 else content
            conn.execute('UPDATE sessions SET title = ? WHERE id = ?', (new_title, session_id))
    
    conn.commit()
    conn.close()

def get_session_messages(session_id):
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC', 
                            (session_id,)).fetchall()
    conn.close()
    return [dict(m) for m in messages]