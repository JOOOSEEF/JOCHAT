// Generar cliente_id si no existe
if (!localStorage.getItem('cliente_id')) {
    localStorage.setItem('cliente_id', 'cliente_' + Math.random().toString(36).substring(2, 10));
}
const cliente_id = localStorage.getItem('cliente_id');

// Estado de escritura en el servidor
// No eliminar: este objeto se gestiona en el backend
typing_status = {};

// Bandera en esta sesión para no reenviar saludo varias veces
let bienvenidaEnviadaSession = false;

function loadMessages() {
    fetch(`/mensajes/${cliente_id}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('chat-messages');
            container.innerHTML = '';

            data.forEach(msg => {
                const div = document.createElement('div');
                div.textContent = `${msg.usuario}: ${msg.texto}`;
                container.appendChild(div);
            });

            container.scrollTop = container.scrollHeight;
        })
        .catch(err => {
            console.error('Error al cargar mensajes:', err);
        });
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    if (!text) return;

    fetch('/mensajes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            cliente_id: cliente_id,
            usuario: "Cliente",
            texto: text
        })
    })
    .then(response => response.json())
    .then(data => {
        input.value = '';
        loadMessages();
    })
    .catch(err => {
        alert('Error al enviar el mensaje');
        console.error(err);
    });
}

// Enviar bienvenida una sola vez en esta sesión
function enviarBienvenida() {
    if (!bienvenidaEnviadaSession) {
        fetch('/mensajes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                cliente_id: cliente_id,
                usuario: "Soporte",
                texto: "👋 Hola, ¿en qué puedo ayudarte?"
            })
        })
        .then(() => {
            bienvenidaEnviadaSession = true;
            loadMessages();
        })
        .catch(err => {
            console.error('Error al enviar mensaje de bienvenida:', err);
        });
    }
}

// Añadimos función para mostrar bienvenida en la UI
let bienvenidaUIMostrada = false;
function showWelcomeInUI() {
    if (!bienvenidaUIMostrada) {
        const container = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.textContent = "👋 Hola, ¿en qué puedo ayudarte?";
        div.className = 'msg msg-agente';
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        bienvenidaUIMostrada = true;
    }
}

// Indicador "escribiendo"
function sendTyping() {
    fetch('/typing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cliente_id })
    }).catch(err => console.error('Error enviando typing:', err));
}

function loadTyping() {
    fetch(`/typing/${cliente_id}`)
        .then(response => response.json())
        .then(data => {
            const indicator = document.getElementById('typing-indicator');
            indicator.style.display = data.typing ? 'block' : 'none';
        })
        .catch(err => console.error('Error cargando typing:', err));
}

// Configurar listener para "escribiendo"
document.getElementById('message-input')
    .addEventListener('input', sendTyping);

// Modificamos toggleChat para incluir el saludo
function toggleChat() {
    chatAbierto = !chatAbierto;
    document.getElementById('chat-container').style.display = chatAbierto ? 'flex' : 'none';
    document.getElementById('chat-bubble').style.display = 'none';
    verificarHorario();

    if (chatAbierto) {
        // Enviar y mostrar bienvenida
        enviarBienvenida();
        showWelcomeInUI();
    }
}

    if (chatAbierto) {
        enviarBienvenida();
    }
}

// Inicia carga de mensajes y typing periódicamente
loadMessages();
setInterval(loadMessages, 3000);
setInterval(loadTyping, 1000);
