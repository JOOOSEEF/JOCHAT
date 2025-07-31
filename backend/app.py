from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(24)
CORS(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'chat.db')

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

def init_db():
    first_time = not os.path.exists(DB_PATH)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT,
                usuario TEXT,
                texto TEXT,
                fecha TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversaciones_asignadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id TEXT UNIQUE,
                agente_nombre TEXT,
                fecha_inicio TEXT
            )
        ''')
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
        # admin por defecto
        cursor.execute(
            'INSERT OR IGNORE INTO agentes (username, password) VALUES (?, ?)',
            ('admin', 'admin123')
        )
        conn.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute('SELECT id FROM agentes WHERE username = ? AND password = ?', (u, p))
            row = cur.fetchone()
        if row:
            user = Agente(row[0], u)
            login_user(user)
            return redirect(url_for('panel_admin'))
        error = True
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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
    cid = data.get('cliente_id', 'anonimo')
    user = data.get('usuario', 'Cliente')
    txt = data.get('texto', '')
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO mensajes (cliente_id, usuario, texto, fecha) VALUES (?, ?, ?, ?)',
            (cid, user, txt, ts)
        )
        conn.commit()
    return jsonify({'status':'ok','fecha':ts})

@app.route('/mensajes/<cliente_id>', methods=['GET'])
def mensajes_por_cliente(cliente_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            'SELECT usuario, texto, fecha FROM mensajes WHERE cliente_id = ? ORDER BY fecha ASC',
            (cliente_id,)
        )
        filas = cur.fetchall()
    return jsonify([{'usuario':u,'texto':t,'fecha':f} for u,t,f in filas])

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT cliente_id FROM mensajes ORDER BY cliente_id')
        filas = cur.fetchall()
    return jsonify([r[0] for r in filas])

@app.route('/conversaciones', methods=['POST'])
def asignar_conversacion():
    data = request.get_json()
    cid = data['cliente_id']
    agente = data['agente_nombre']
    inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT OR REPLACE INTO conversaciones_asignadas (cliente_id, agente_nombre, fecha_inicio) VALUES (?,?,?)',
            (cid, agente, inicio)
        )
        conn.commit()
    return jsonify({'status':'ok'})

@app.route('/conversaciones', methods=['GET'])
def obtener_asignaciones():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT cliente_id, agente_nombre, fecha_inicio FROM conversaciones_asignadas')
        filas = cur.fetchall()
    return jsonify([{'cliente_id':c,'agente_nombre':a,'fecha_inicio':f} for c,a,f in filas])

@app.route('/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json()
    nombre   = data.get('nombre','')
    email    = data.get('email','')
    telefono = data.get('telefono','')
    mensaje  = data.get('mensaje','')
    cid      = data.get('cliente_id', None)
    ts       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO tickets (cliente_id,nombre,email,telefono,mensaje,fecha) VALUES (?,?,?,?,?,?)',
            (cid,nombre,email,telefono,mensaje,ts)
        )
        conn.commit()
    return jsonify({'status':'ok'})

@app.route('/tickets', methods=['GET'])
def listar_tickets():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('SELECT id,cliente_id,nombre,email,telefono,mensaje,fecha,atendido FROM tickets ORDER BY fecha DESC')
        filas = cur.fetchall()
    out=[]
    for i,c,n,e,t,m,f,a in filas:
        out.append({'id':i,'cliente_id':c,'nombre':n,'email':e,'telefono':t,'mensaje':m,'fecha':f,'atendido':bool(a)})
    return jsonify(out)

@app.route('/tickets/<int:ticket_id>', methods=['POST'])
def marcar_atendido(ticket_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('UPDATE tickets SET atendido=1 WHERE id=?',(ticket_id,))
        conn.commit()
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
