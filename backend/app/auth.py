# backend/app/auth.py

from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from app.models import Agente

# Indicamos que las plantillas están en backend/app/templates/
auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        # Autentica contra la base de datos
        user = Agente.authenticate(username, password)
        if user:
            login_user(user)
            # Redirige al panel de admin una vez logado
            return redirect(url_for('admin.panel'))
        error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    message = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            error = 'Usuario y contraseña obligatorios'
        else:
            agent, err = Agente.register(username, password)
            if err:
                error = err
            else:
                message = 'Agente registrado con éxito. Ya puedes iniciar sesión.'
    return render_template('register.html', error=error, message=message)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
