from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

# App Flask
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, static_folder='static', template_folder=template_dir)
app.secret_key = os.urandom(24)
CORS(app)

# Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# DB path
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

# Usuario para Login
class Agente(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username FROM agentes WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return Agente(row[0], row[1])
    return None

# Crear DB y tablas
def init_db():
    need_seed = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS agentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT,
            usuario TEXT,
            texto TEXT,
            fecha TEXT
        )
    ''')
    c.execute('''
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversaciones_asignadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT UNIQUE,
            agente_nombre TEXT,
            fecha_inicio TEXT
        )
    ''')
    conn.commit()
    # Seed default agent
    if need_seed:
        hashed = generate_password_hash('password123')
        c.execute('INSERT OR IGNORE INTO agentes (username, password) VALUES (?, ?)', ('admin', hashed))
        conn.commit()
    conn.close()

# --- Rutas de autenticación ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, password FROM agentes WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        if row and check_password_hash(row[1], password):
            user = Agente(row[0], username)
            login_user(user)
            return redirect(url_for('panel_admin'))
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Vistas básicas ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
@login_required
def panel_admin():
    return render_template('admin.html', agente=current_user.username)

# --- Mensajes ---
@app.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    cliente_id = data.get('cliente_id', 'anonimo')
    usuario = data.get('usuario', 'Cliente')
    texto = data.get('texto', '')
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO mensajes (cliente_id, usuario, texto, fecha) VALUES (?, ?, ?, ?)',
              (cliente_id, usuario, texto, fecha))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok', 'fecha': fecha})

@app.route('/mensajes/<cliente_id>', methods=['GET'])
def mensajes_por_cliente(cliente_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT usuario, texto, fecha FROM mensajes WHERE cliente_id = ? ORDER BY fecha ASC', (cliente_id,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{'usuario': u, 'texto': t, 'fecha': f} for u, t, f in rows])

# --- Clientes ---
@app.route('/clientes', methods=['GET'])
@login_required
def listar_clientes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT DISTINCT cliente_id FROM mensajes ORDER BY cliente_id ASC')
    rows = c.fetchall()
    conn.close()
    return jsonify([r[0] for r in rows])

# --- Conversaciones ---
@app.route('/conversaciones', methods=['POST'])
@login_required
def asignar_conversacion():
    data = request.get_json()
    cliente_id = data['cliente_id']
    agente_nombre = data['agente_nombre']
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO conversaciones_asignadas (cliente_id, agente_nombre, fecha_inicio) VALUES (?, ?, ?)',
              (cliente_id, agente_nombre, fecha))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/conversaciones', methods=['GET'])
@login_required
def obtener_asignaciones():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT cliente_id, agente_nombre, fecha_inicio FROM conversaciones_asignadas')
    rows = c.fetchall()
    conn.close()
    return jsonify([{'cliente_id': c0, 'agente_nombre': a, 'fecha_inicio': f} for c0, a, f in rows])

# --- Tickets ---
@app.route('/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json()
    nombre = data.get('nombre', '')
    email = data.get('email', '')
    telefono = data.get('telefono', '')
    mensaje = data.get('mensaje', '')
    cliente_id = data.get('cliente_id', None)
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO tickets (cliente_id, nombre, email, telefono, mensaje, fecha) VALUES (?, ?, ?, ?, ?, ?)',
              (cliente_id, nombre, email, telefono, mensaje, fecha))
    conn.commit()
    tid = c.lastrowid
    conn.close()
    return jsonify({'status': 'ok', 'ticket_id': tid})

@app.route('/tickets', methods=['GET'])
@login_required
def listar_tickets():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, cliente_id, nombre, email, telefono, mensaje, fecha, atendido FROM tickets ORDER BY fecha DESC')
    rows = c.fetchall()
    conn.close()
    tickets = []
    for id_, cid, n, e, t, m, f, a in rows:
        tickets.append({'id': id_, 'cliente_id': cid, 'nombre': n,
                        'email': e, 'telefono': t, 'mensaje': m,
                        'fecha': f, 'atendido': bool(a)})
    return jsonify(tickets)

@app.route('/tickets/<int:ticket_id>', methods=['POST'])
@login_required
def marcar_atendido(ticket_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE tickets SET atendido = 1 WHERE id = ?', (ticket_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
