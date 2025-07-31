import os
from dotenv import load_dotenv

# Carga variables de entorno desde .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'cambia_est0')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, '..', 'chat.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
