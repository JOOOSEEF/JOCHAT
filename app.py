
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde frontend local

DB_PATH = '../database/chat.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT,
                texto TEXT,
                fecha TEXT
            )
        ''')
        conn.commit()

@app.route('/mensajes', methods=['GET'])
def obtener_mensajes():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, texto, fecha FROM mensajes ORDER BY fecha ASC")
        mensajes = cursor.fetchall()
    return jsonify([{"usuario": u, "texto": t, "fecha": f} for u, t, f in mensajes])

@app.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    usuario = data.get("usuario", "Cliente")
    texto = data.get("texto", "")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mensajes (usuario, texto, fecha) VALUES (?, ?, ?)", (usuario, texto, fecha))
        conn.commit()

    return jsonify({"status": "ok", "fecha": fecha})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
