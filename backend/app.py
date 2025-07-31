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

# Crear base de datos si no existe (con cliente_id)
def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT,
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

# Obtener todos los mensajes (usado antes)
@app.route('/mensajes', methods=['GET'])
def obtener_mensajes():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, texto, fecha FROM mensajes ORDER BY fecha ASC")
        mensajes = cursor.fetchall()
    return jsonify([{"usuario": u, "texto": t, "fecha": f} for u, t, f in mensajes])

# Obtener mensajes por cliente (nuevo)
@app.route('/mensajes/<cliente_id>', methods=['GET'])
def mensajes_por_cliente(cliente_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, texto, fecha FROM mensajes WHERE cliente_id = ? ORDER BY fecha ASC", (cliente_id,))
        mensajes = cursor.fetchall()
    return jsonify([{"usuario": u, "texto": t, "fecha": f} for u, t, f in mensajes])

# Obtener lista de clientes únicos (nuevo)
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cliente_id FROM mensajes ORDER BY cliente_id ASC")
        clientes = [row[0] for row in cursor.fetchall()]
    return jsonify(clientes)

# Guardar mensaje nuevo (añadido cliente_id)
@app.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    cliente_id = data.get("cliente_id", "anonimo")
    usuario = data.get("usuario", "Cliente")
    texto = data.get("texto", "")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mensajes (cliente_id, usuario, texto, fecha) VALUES (?, ?, ?, ?)",
                       (cliente_id, usuario, texto, fecha))
        conn.commit()

    return jsonify({"status": "ok", "fecha": fecha})

# Iniciar el servidor
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Para Render
    app.run(debug=False, host='0.0.0.0', port=port)
