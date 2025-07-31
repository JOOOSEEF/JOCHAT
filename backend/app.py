```python
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from datetime import datetime
import os

# Inicializar Flask y permitir CORS
auth_app = Flask(__name__, static_folder='static', template_folder='templates')
auth_app.secret_key = os.urandom(24)
CORS(auth_app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(auth_app)

# Ruta absoluta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

# User class para Flask-Login
class Agente(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, username FROM agentes WHERE id = ?', (user_id,))
        row = cur.fetchone()
    if row:
        return Agente(row[0], row[1])
    return None

# Crear base de datos y tablas si no existen
def init_db():
    first_time = not os.path.exists(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT,
                usuario TEXT,
                texto TEXT,
                fecha TEXT
            )
        ''')
        # Tickets
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
        # Conversaciones asignadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones_asignadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT UNIQUE,
                agente_nombre TEXT,
                fecha_inicio TEXT
            )
        ''')
        # Agentes y admin por defecto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        # Insertar un admin por defecto si no existe
        cursor.execute(
            'INSERT OR IGNORE INTO agentes (username, password) VALUES (?, ?)',
            ('admin', 'admin123')
        )
        conn.commit()

# Rutas de autenticación
@auth_app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id FROM agentes WHERE username = ? AND password = ?', (username, password))
            row = cur.fetchone()
        if row:
            user = Agente(row[0], username)
            login_user(user)
            return redirect(url_for('panel_admin'))
        error = True
    return render_template('login.html', error=error)

@auth_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas de la aplicación
auth_app.route('/')(policy=lambda f: f)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
@login_required
def panel_admin():
    return render_template('admin.html', agente=current_user.username)

@app.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    cliente_id = data.get('cliente_id', 'anonimo')
    usuario = data.get('usuario', 'Cliente')
    texto = data.get('texto', '')
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO mensajes (cliente_id, usuario, texto, fecha) VALUES (?, ?, ?, ?)',
            (cliente_id, usuario, texto, fecha)
        )
        conn.commit()
    return jsonify({'status': 'ok', 'fecha': fecha})

@app.route('/mensajes/<cliente_id>', methods=['GET'])
def mensajes_por_cliente(cliente_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT usuario, texto, fecha FROM mensajes WHERE cliente_id = ? ORDER BY fecha ASC',
            (cliente_id,)
        )
        filas = cursor.fetchall()
    return jsonify([{'usuario': u, 'texto': t, 'fecha': f} for u, t, f in filas])

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT cliente_id FROM mensajes ORDER BY cliente_id ASC')
        filas = cursor.fetchall()
    return jsonify([row[0] for row in filas])

@app.route('/conversaciones', methods=['POST'])
def asignar_conversacion():
    data = request.get_json()
    cliente_id = data['cliente_id']
    agente_nombre = data['agente_nombre']
    fecha_inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO conversaciones_asignadas (cliente_id, agente_nombre, fecha_inicio) VALUES (?, ?, ?)',
            (cliente_id, agente_nombre, fecha_inicio)
        )
        conn.commit()
    return jsonify({'status': 'ok'})

@app.route('/conversaciones', methods=['GET'])
def obtener_asignaciones():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT cliente_id, agente_nombre, fecha_inicio FROM conversaciones_asignadas')
        filas = cursor.fetchall()
    return jsonify([{'cliente_id': c, 'agente_nombre': a, 'fecha_inicio': f} for c, a, f in filas])

@app.route('/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json()
    nombre = data.get('nombre', '')
    email = data.get('email', '')
    telefono = data.get('telefono', '')
    mensaje = data.get('mensaje', '')
    cliente_id = data.get('cliente_id', None)
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO tickets (cliente_id, nombre, email, telefono, mensaje, fecha) VALUES (?, ?, ?, ?, ?, ?)',
            (cliente_id, nombre, email, telefono, mensaje, fecha)
        )
        conn.commit()
    return jsonify({'status': 'ok'})

@app.route('/tickets', methods=['GET'])
def listar_tickets():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, cliente_id, nombre, email, telefono, mensaje, fecha, atendido FROM tickets ORDER BY fecha DESC')
        filas = cursor.fetchall()
    tickets = []
    for id_, cid, n, e, t, m, f, a in filas:
        tickets.append({
            'id': id_, 'cliente_id': cid, 'nombre': n,
            'email': e, 'telefono': t, 'mensaje': m,
            'fecha': f, 'atendido': bool(a)
        })
    return jsonify(tickets)

@app.route('/tickets/<int:ticket_id>', methods=['POST'])
def marcar_atendido(ticket_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE tickets SET atendido = 1 WHERE id = ?', (ticket_id,))
        conn.commit()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    auth_app.run(debug=False, host='0.0.0.0', port=port)
```
