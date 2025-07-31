# backend/app/models.py

import sqlite3
from datetime import datetime
from flask_login import UserMixin
from app.config import Config  # antes era from config import Config

def get_conn():
    """Get a sqlite3 connection with row_factory set to dict-like rows."""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class Agente(UserMixin):
    """User/agent model for Flask-Login."""

    def __init__(self, id_, username):
        self.id = id_
        self.username = username

    @staticmethod
    def create_table():
        with get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )
            ''')

    @staticmethod
    def get_by_id(agent_id):
        row = get_conn().execute(
            'SELECT id, username FROM agentes WHERE id = ?',
            (agent_id,)
        ).fetchone()
        return Agente(row['id'], row['username']) if row else None

    @staticmethod
    def authenticate(username, password):
        row = get_conn().execute(
            'SELECT id FROM agentes WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        return Agente(row['id'], username) if row else None

    @staticmethod
    def register(username, password):
        """Return (agent, None) or (None, error_msg)."""
        try:
            with get_conn() as conn:
                cur = conn.execute(
                    'INSERT INTO agentes (username, password) VALUES (?, ?)',
                    (username, password)
                )
                return Agente(cur.lastrowid, username), None
        except sqlite3.IntegrityError:
            return None, 'Ese usuario ya existe'

class Mensaje:
    """Chat message model."""

    @staticmethod
    def create_table():
        with get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT,
                    usuario TEXT,
                    texto TEXT,
                    fecha TEXT
                )
            ''')

    @staticmethod
    def add(cliente_id, usuario, texto):
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            conn.execute(
                'INSERT INTO mensajes (cliente_id, usuario, texto, fecha) VALUES (?, ?, ?, ?)',
                (cliente_id, usuario, texto, fecha)
            )
        return fecha

    @staticmethod
    def all_for(cliente_id):
        rows = get_conn().execute(
            'SELECT usuario, texto, fecha FROM mensajes WHERE cliente_id = ? ORDER BY fecha ASC',
            (cliente_id,)
        ).fetchall()
        return [dict(r) for r in rows]

class ConversacionAsignada:
    """Assigned conversation (who is handling which cliente_id)."""

    @staticmethod
    def create_table():
        with get_conn() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversaciones_asignadas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id TEXT UNIQUE,
                    agente_nombre TEXT,
                    fecha_inicio TEXT
                )
            ''')

    @staticmethod
    def assign(cliente_id, agente_nombre):
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            conn.execute(
                'INSERT OR REPLACE INTO conversaciones_asignadas '
                '(cliente_id, agente_nombre, fecha_inicio) VALUES (?, ?, ?)',
                (cliente_id, agente_nombre, fecha)
            )

    @staticmethod
    def all():
        rows = get_conn().execute(
            'SELECT cliente_id, agente_nombre, fecha_inicio FROM conversaciones_asignadas'
        ).fetchall()
        return [dict(r) for r in rows]

class Ticket:
    """Offline ticket model for out-of-hours messages."""

    @staticmethod
    def create_table():
        with get_conn() as conn:
            conn.execute('''
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

    @staticmethod
    def create(cliente_id, nombre, email, telefono, mensaje):
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with get_conn() as conn:
            cur = conn.execute(
                'INSERT INTO tickets '
                '(cliente_id, nombre, email, telefono, mensaje, fecha) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (cliente_id, nombre, email, telefono, mensaje, fecha)
            )
        return cur.lastrowid

    @staticmethod
    def all():
        rows = get_conn().execute(
            'SELECT id, cliente_id, nombre, email, telefono, mensaje, fecha, atendido '
            'FROM tickets ORDER BY fecha DESC'
        ).fetchall()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_attended(ticket_id):
        with get_conn() as conn:
            conn.execute(
                'UPDATE tickets SET atendido = 1 WHERE id = ?',
                (ticket_id,)
            )
