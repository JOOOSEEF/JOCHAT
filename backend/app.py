from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
from flask_cors import CORS
import os

# Inicializar Flask y permitir CORS
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Ruta absoluta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

# Crear base de datos si no existe
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

# Ruta principal del chat (cliente)
@app.route('/')
def home():
    return render_template('index.html')

# Ruta del panel de administración
@app.route('/admin')
def panel_admin():
    return render_template('admin.html')

# Obtener todos los mensajes
@app.route('/mensajes', methods=['GET'])
def obtener_mensajes():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, texto, fecha FROM mensajes ORDER BY fecha ASC")
        mensajes = cursor.fetchall()
    return jsonify([{"usuario": u, "texto": t, "fecha": f} for u, t, f in mensajes])

# Guardar mensaje nuevo
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

# Iniciar el servidor
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Para Render
    app.run(debug=False, host='0.0.0.0', port=port)
