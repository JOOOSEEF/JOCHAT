import os
from flask import Flask, render_template
from app.config import Config
from app import db
from app.models import Agente, Mensaje, ConversacionAsignada, Ticket
from sqlalchemy import text

def create_app():
    # Creamos la app indicando carpetas de templates y estáticos
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static')
    )
    app.config.from_object(Config)

    # Inicializamos SQLAlchemy (aunque luego usemos sqlite3 directly para ciertas tablas)
    db.init_app(app)

    with app.app_context():
        # Ruta al fichero de base de datos
        db_file = os.path.join(app.config['BASE_DIR'], '..', 'chat.db')
        if not os.path.exists(db_file):
            # Crea el fichero sqlite vacío
            open(db_file, 'w').close()

            # Si quisieras ejecutar un schema.sql con múltiples sentencias:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path) as f:
                sql_statements = f.read()
            for stmt in filter(None, (s.strip() for s in sql_statements.split(';'))):
                db.session.execute(text(stmt))
            db.session.commit()

            # Y/o crea tablas con tus propios métodos de modelos sqlite3
            Agente.create_table()
            Mensaje.create_table()
            ConversacionAsignada.create_table()
            Ticket.create_table()

    # Registro de blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.chat_api import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)

    # Ruta principal
    @app.route('/')
    def home():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
