# backend/chat_api.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from models import Mensaje, ConversacionAsignada, Ticket

chat_bp = Blueprint('chat', __name__, url_prefix='/api')

@chat_bp.route('/mensajes', methods=['POST'])
def guardar_mensaje():
    data = request.get_json()
    cid = data.get('cliente_id', 'anonimo')
    usuario = data.get('usuario', 'Cliente')
    texto = data.get('texto', '')
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = Mensaje.create(cliente_id=cid, usuario=usuario, texto=texto, fecha=fecha)
    return jsonify({'status': 'ok', 'mensaje_id': msg.id, 'fecha': fecha})

@chat_bp.route('/mensajes/<cliente_id>', methods=['GET'])
@login_required  # only logged-in agents can fetch chat histories
def mensajes_por_cliente(cliente_id):
    rows = Mensaje.get_by_cliente(cliente_id)
    return jsonify([r.to_dict() for r in rows])

@chat_bp.route('/clientes', methods=['GET'])
@login_required
def listar_clientes():
    clientes = Mensaje.list_clientes()
    return jsonify(clientes)

@chat_bp.route('/conversaciones', methods=['POST'])
@login_required
def asignar_conversacion():
    data = request.get_json()
    cid = data['cliente_id']
    agente = current_user.username
    inicio = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conv = ConversacionAsignada.upsert(cliente_id=cid, agente_nombre=agente, fecha_inicio=inicio)
    return jsonify({'status': 'ok', 'conversacion_id': conv.id})

@chat_bp.route('/conversaciones', methods=['GET'])
@login_required
def obtener_asignaciones():
    rows = ConversacionAsignada.list_all()
    return jsonify([r.to_dict() for r in rows])

@chat_bp.route('/tickets', methods=['POST'])
def crear_ticket():
    data = request.get_json()
    t = Ticket.create(
        cliente_id=data.get('cliente_id'),
        nombre=data.get('nombre', ''),
        email=data.get('email', ''),
        telefono=data.get('telefono', ''),
        mensaje=data.get('mensaje', ''),
        fecha=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    return jsonify({'status': 'ok', 'ticket_id': t.id})

@chat_bp.route('/tickets', methods=['GET'])
@login_required
def listar_tickets():
    rows = Ticket.list_all()
    return jsonify([r.to_dict() for r in rows])

@chat_bp.route('/tickets/<int:ticket_id>/atender', methods=['POST'])
@login_required
def marcar_atendido(ticket_id):
    Ticket.mark_as_attended(ticket_id)
    return jsonify({'status': 'ok'})
