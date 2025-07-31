# backend/app/chat_api.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime

# Antes: from models import Mensaje, ConversacionAsignada, Ticket
# Ahora importamos desde el paquete app:
from app.models import Mensaje, ConversacionAsignada, Ticket

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    cid = data.get('cliente_id', 'anonimo')
    usuario = data.get('usuario', 'Cliente')
    texto = data.get('texto', '')
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg_id = Mensaje.add(cliente_id=cid, usuario=usuario, texto=texto)
    return jsonify({'status': 'ok', 'mensaje_id': msg_id, 'fecha': fecha})

@chat_bp.route('/mensajes/<cliente_id>', methods=['GET'])
@login_required  # sólo agentes logados pueden ver el historial
def mensajes_por_cliente(cliente_id):
    rows = Mensaje.all_for(cliente_id)
    return jsonify(rows)

@chat_bp.route('/clientes', methods=['GET'])
@login_required
def listar_clientes():
    # Si necesitas agrupar por cliente:
    clientes = Mensaje.list_clientes()  # o implementa tu método
    return jsonify(clientes)

@chat_bp.route('/conversaciones', methods=['POST'])
@login_required
def asignar_conversacion():
    data = request.get_json()
    cid = data['cliente_id']
    agente = current_user.username
    inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ConversacionAsignada.assign(cliente_id=cid, agente_nombre=agente)
    return jsonify({'status': 'ok', 'cliente_id': cid, 'agente': agente, 'inicio': inicio})

@chat_bp.route('/conversaciones', methods=['GET'])
@login_required
def obtener_asignaciones():
    rows = ConversacionAsignada.all()
    return jsonify(rows)

@chat_bp.route('/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json()
    t_id = Ticket.create(
        cliente_id=data.get('cliente_id'),
        nombre=data.get('nombre', ''),
        email=data.get('email', ''),
        telefono=data.get('telefono', ''),
        mensaje=data.get('mensaje', '')
    )
    return jsonify({'status': 'ok', 'ticket_id': t_id})

@chat_bp.route('/tickets', methods=['GET'])
@login_required
def listar_tickets():
    rows = Ticket.all()
    return jsonify(rows)

@chat_bp.route('/tickets/<int:ticket_id>/atender', methods=['POST'])
@login_required
def marcar_atendido(ticket_id):
    Ticket.mark_attended(ticket_id)
    return jsonify({'status': 'ok'})
