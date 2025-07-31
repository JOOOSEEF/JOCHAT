import os
from flask import Flask, render_template
from app.config import Config
from app import db
from sqlalchemy import text

def create_app():
    # indicamos dónde están templates y static
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static')
    )
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db_file = os.path.join(app.config['BASE_DIR'], '..', 'chat.db')
        if not os.path.exists(db_file):
            # Crea las tablas definidas por SQLAlchemy (modelos)
            db.create_all()

            # Lee y ejecuta cada sentencia del schema SQL
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path) as f:
                sql_statements = f.read()

            # Divide por ';' y ejecuta cada bloque no vacío
            for stmt in filter(None, (s.strip() for s in sql_statements.split(';'))):
                db.session.execute(text(stmt))

            db.session.commit()

    # Registro de blueprints
    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.chat_api import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)

    # Ruta principal: sirve index.html
    @app.route('/')
    def home():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
