# backend/app/admin.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Ahora las plantillas están en backend/app/templates/
admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='templates'
)

@admin_bp.route('/')
@login_required
def panel():
    """
    Panel principal de administración donde los agentes verán
    las conversaciones, tickets y configuración.
    """
    return render_template('admin.html', agente=current_user.username)

@admin_bp.route('/snippet')
@login_required
def snippet():
    """
    Página que muestra el código de embebido (snippet) que el tenant
    debe copiar en su web para activar el widget.
    Se pasa el identificador único del tenant (por simplicidad, el username).
    """
    tenant_id = current_user.username
    return render_template('embed_script.html', tenant=tenant_id)
