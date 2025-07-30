from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Permitir peticiones desde frontend

# Base de datos en raíz del proyecto, compatible con Render
DB_PATH = os.path.join(os.getcwd(), 'chat.db')

def init_db():
    if not os.path.exists(DB_PATH):
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
    port = int(os.environ.get("PORT", 5000))  # Necesario para Render
    app.run(debug=False, host='0.0.0.0', port=port)

