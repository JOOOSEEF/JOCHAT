import os
from flask import Flask
from app.config import Config
from app import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db_file = os.path.join(app.config['BASE_DIR'], '..', 'chat.db')
        if not os.path.exists(db_file):
            db.create_all()
            with open(os.path.join(os.path.dirname(__file__), 'schema.sql')) as f:
                db.session.execute(f.read())
                db.session.commit()

    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.chat_api import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
