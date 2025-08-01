import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'chat.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Función para crear las tablas si no existen
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

# Asegurar que las tablas existen en cada arranque
def initialize_app():
    create_tables()

initialize_app()

@app.route('/messages', methods=['POST'])
def add_message():
    data = request.get_json()
    username = data.get('username')
    content = data.get('content')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (username) VALUES (?)", (username,)
    )
    cursor.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    )
    user_id = cursor.fetchone()['id']
    cursor.execute(
        "INSERT INTO messages (user_id, content) VALUES (?, ?)",
        (user_id, content)
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'}), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    conn = get_db_connection()
    messages = conn.execute(
        "SELECT u.username, m.content, m.timestamp FROM messages m JOIN users u ON m.user_id = u.id ORDER BY m.timestamp DESC"
    ).fetchall()
    conn.close()

    result = [dict(msg) for msg in messages]

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
