from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
from flask_cors import CORS
import os

# Inicializar Flask y permitir CORS\app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Ruta absoluta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

# Crear base de datos y tablas si no existen
def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Tabla de mensajes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT,
                    usuario TEXT,
                    texto TEXT,
                    fecha TEXT
                )
            ''')
            # Tabla de tickets fuera de horario
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT,
                    nombre TEXT,
                    email TEXT,
                    telefono TEXT,
                    mensaje TEXT,
                    fecha TEXT,
                    atendido INTEGER DEFAULT 0
                )
            ''')
            # Tabla de asignaciones de conversación
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversaciones_asignadas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT UNIQUE,
                    agente_nombre TEXT,
                    fecha_inicio TEXT
                )
            ''')
            conn.commit()

# Ruta principal del chat (cliente)
@app.route('/')
def home():
    return render_template('index.html')

# Ruta del panel de administración\@app.route('/admin')
def panel_admin():
    return render_template('admin.html')

# Endpoints de Mensajes
@app.route('/mensajes/<cliente_id>', methods=['GET'])
def mensajes_por_cliente(cliente_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT usuario, texto, fecha FROM mensajes WHERE cliente_id = ? ORDER BY fecha ASC", (cliente_id,))
        mensajes = cursor.fetchall()
    return jsonify([{"usuario": u, "texto": t, "fecha": f} for u, t, f in mensajes])

@app.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    cliente_id = data.get("cliente_id", "anonimo")
    usuario = data.get("usuario", "Cliente")
    texto = data.get("texto", "")
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO mensajes (cliente_id, usuario, texto, fecha) VALUES (?, ?, ?, ?)",
            (cliente_id, usuario, texto, fecha)
        )
        conn.commit()
    return jsonify({"status": "ok", "fecha": fecha})

# Endpoints de Clientes y Conversaciones Asignadas
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cliente_id FROM mensajes ORDER BY cliente_id ASC")
        clientes = [row[0] for row in cursor.fetchall()]
    return jsonify(clientes)

@app.route('/conversaciones', methods=['POST'])
def asignar_conversacion():
    data = request.get_json()
    cliente_id = data.get("cliente_id")
    agente_nombre = data.get("agente_nombre")
    fecha_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO conversaciones_asignadas (cliente_id, agente_nombre, fecha_inicio) VALUES (?, ?, ?)",
            (cliente_id, agente_nombre, fecha_inicio)
        )
        conn.commit()
    return jsonify({"status": "ok"})

@app.route('/conversaciones', methods=['GET'])
def obtener_asignaciones():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT cliente_id, agente_nombre, fecha_inicio FROM conversaciones_asignadas")
        filas = cursor.fetchall()
    return jsonify([{"cliente_id": c, "agente_nombre": a, "fecha_inicio": f} for c, a, f in filas])

# Endpoints de Tickets
@app.route('/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json()
    nombre = data.get("nombre", "")
    email = data.get("email", "")
    telefono = data.get("telefono", "")
    mensaje = data.get("mensaje", "")
    cliente_id = data.get("cliente_id", None)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (cliente_id, nombre, email, telefono, mensaje, fecha) VALUES (?, ?, ?, ?, ?, ?)",
            (cliente_id, nombre, email, telefono, mensaje, fecha)
        )
        conn.commit()
        ticket_id = cursor.lastrowid
    return jsonify({"status": "ok", "ticket_id": ticket_id})

@app.route('/tickets', methods=['GET'])
def listar_tickets():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente_id, nombre, email, telefono, mensaje, fecha, atendido FROM tickets ORDER BY fecha DESC")
        filas = cursor.fetchall()
    tickets = []
    for id_, cid, n, e, t, m, f, a in filas:
        tickets.append({
            "id": id_, "cliente_id": cid, "nombre": n,
            "email": e, "telefono": t, "mensaje": m,
            "fecha": f, "atendido": bool(a)
        })
    return jsonify(tickets)

@app.route('/tickets/<int:ticket_id>', methods=['POST'])
def marcar_atendido(ticket_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET atendido = 1 WHERE id = ?", (ticket_id,))
        conn.commit()
    return jsonify({"status": "ok"})

# Iniciar el servidor
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Para Render
    app.run(debug=False, host='0.0.0.0', port=port)
