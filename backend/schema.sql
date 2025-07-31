-- Tablas de agentes, conversaciones y mensajes
CREATE TABLE agentes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  rol TEXT DEFAULT 'user'
);

CREATE TABLE conversaciones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  usuario TEXT NOT NULL,
  iniciado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mensajes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversacion_id INTEGER NOT NULL,
  remitente TEXT NOT NULL,
  contenido TEXT NOT NULL,
  enviado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(conversacion_id) REFERENCES conversaciones(id)
);
