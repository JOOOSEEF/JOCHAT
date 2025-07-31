from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

# Inicializar Flask
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, static_folder='static', template_folder=template_dir)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
CORS(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

# Modelo de usuario Agente
class Agente(UserMixin):
    def __init__(self, id_, username):
        self.id = id_
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, username FROM agentes WHERE id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return Agente(row[0], row[1]) if row else None

# Crear tablas iniciales
def init_db():
    first_run = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Tabla agentes
    cur.execute('''
        CREATE TABLE IF NOT EXISTS agentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    # Tabla mensajes
    cur.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT,
            usuario TEXT,
            texto TEXT,
            fecha TEXT
        )
    ''')
    # Tabla conversaciones asignadas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS conversaciones_asignadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id TEXT UNIQUE,
            agente_nombre TEXT,
            fecha_inicio TEXT
        )
    ''')
    # Tabla tickets
    cur.execute('''
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
    # Agregar admin por defecto
    if first_run:
        pwd = generate_password_hash('admin123')
        cur.execute('INSERT OR IGNORE INTO agentes (username, password_hash) VALUES (?, ?)', ('admin', pwd))
    conn.commit()
    conn.close()

# Ruta de login (GET y POST)
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password'].strip()
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT id, password_hash FROM agentes WHERE username = ?', (u,))
        row = cur.fetchone()
        conn.close()
        if row and check_password_hash(row[1], p):
            user = Agente(row[0], u)
            login_user(user)
            return redirect(url_for('panel_admin'))
        error = True
    return render_template('login.html', error=error)

# Ruta de registro (GET y POST)
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    message = None
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password'].strip()
        if not u or not p:
            error = 'Usuario y contraseña obligatorios'
        else:
            pwd_hash = generate_password_hash(p)
            try:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute('INSERT INTO agentes (username, password_hash) VALUES (?, ?)', (u, pwd_hash))
                conn.commit()
                conn.close()
                message = 'Agente registrado con éxito'
            except sqlite3.IntegrityError:
                error = 'Ese usuario ya existe'
    return render_template('register.html', error=error, message=message)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas principales
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def panel_admin():
    return render_template('admin.html', agente=current_user.username)

# Resto de endpoints (mensajes, clientes, conversaciones, tickets) quedan igual

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
