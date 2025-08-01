 import os
 from flask import Flask, render_template
-from app.config import Config
-from app import db
+from app.config import Config
 from sqlalchemy import text

 def create_app():
     app = Flask(
         __name__,
         template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
         static_folder=os.path.join(os.path.dirname(__file__), 'static')
     )
     app.config.from_object(Config)

-    db.init_app(app)
-
-    with app.app_context():
-        db_file = os.path.join(app.config['BASE_DIR'], '..', 'chat.db')
-        if not os.path.exists(db_file):
-            # Crea las tablas definidas por SQLAlchemy (modelos)
-            db.create_all()
-
-            # Lee y ejecuta cada sentencia del schema SQL
-            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
-            with open(schema_path) as f:
-                sql_statements = f.read()
-
-            # Divide por ';' y ejecuta cada bloque no vacío
-            for stmt in filter(None, (s.strip() for s in sql_statements.split(';'))):
-                db.session.execute(text(stmt))
-
-            db.session.commit()
+    # Dado que estás usando sqlite3 directamente, llama aquí a los create_table()
+    from app.models import Agente, Mensaje, ConversacionAsignada, Ticket
+
+    db_file = os.path.join(app.config['BASE_DIR'], '..', 'chat.db')
+    if not os.path.exists(db_file):
+        # Crea el archivo
+        open(db_file, 'w').close()
+        # Ahora crea cada tabla con tus propios métodos
+        Agente.create_table()
+        Mensaje.create_table()
+        ConversacionAsignada.create_table()
+        Ticket.create_table()

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
