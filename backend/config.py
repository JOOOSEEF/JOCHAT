import os

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    # Clave secreta para sesiones y Flask-Login
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cambia-esta-clave-en-produccion')

    # Ruta al fichero SQLite
    DB_PATH = os.path.join(BASE_DIR, 'chat.db')

    # Horario de atención (puedes parametrizar si quieres)
    OFFICE_HOUR_START = 9   # 9am
    OFFICE_HOUR_END   = 18  # 6pm

    # Aquí podrías añadir más settings, p.ej. dominios permitidos, etc.
