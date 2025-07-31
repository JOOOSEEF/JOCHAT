// Generar cliente_id si no existe
if (!localStorage.getItem('cliente_id')) {
    localStorage.setItem('cliente_id', 'cliente_' + Math.random().toString(36).substring(2, 10));
}
const cliente_id = localStorage.getItem('cliente_id');

let chatAbierto = false;
let bienvenidaEnviada = false;
let bienvenidaUIMostrada = false;
let mensajesInterval;
let typingInterval;

function loadMessages() {
    fetch(`/mensajes/${cliente_id}`)
        .then(res => res.json())
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
        .catch(err => console.error('Error cargando mensajes:', err));
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const text = input.value.trim();
    if (!text) return;
    fetch('/mensajes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cliente_id, usuario: 'Cliente', texto: text })
    })
    .then(res => res.json())
    .then(() => {
        input.value = '';
        loadMessages();
    })
    .catch(err => console.error('Error enviando:', err));
}

function enviarBienvenida() {
    if (!bienvenidaEnviada) {
        fetch('/mensajes', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cliente_id, usuario: 'Soporte', texto: '👋 Hola, ¿en qué puedo ayudarte?' })
        })
        .then(() => {
            bienvenidaEnviada = true;
            showWelcomeInUI();
        })
        .catch(err => console.error('Error saludo:', err));
    }
}

function showWelcomeInUI() {
    if (!bienvenidaUIMostrada) {
        const container = document.getElementById('chat-messages');
        const div = document.createElement('div');
        div.textContent = '👋 Hola, ¿en qué puedo ayudarte?';
        div.style.fontStyle = 'italic';
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        bienvenidaUIMostrada = true;
    }
}

function sendTyping() {
    fetch('/typing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cliente_id })
    }).catch(err => console.error('Error typing:', err));
}

function loadTyping() {
    fetch(`/typing/${cliente_id}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('typing-indicator').style.display = data.typing ? 'block' : 'none';
        })
        .catch(err => console.error('Error cargar typing:', err));
}

// Abrir/Cerrar chat
document.getElementById('chat-button').addEventListener('click', () => {
    chatAbierto = !chatAbierto;
    const container = document.getElementById('chat-container');
    container.style.display = chatAbierto ? 'flex' : 'none';
    document.getElementById('chat-bubble').style.display = 'none';
    if (chatAbierto) {
        enviarBienvenida();
        loadMessages();
        typingInterval = setInterval(loadTyping, 1000);
        mensajesInterval = setInterval(loadMessages, 3000);
    } else {
        clearInterval(typingInterval);
        clearInterval(mensajesInterval);
    }
});

// Configurar listener para escritura
const inputEl = document.getElementById('message-input');
inputEl && inputEl.addEventListener('input', sendTyping);

// Al cargar:
window.addEventListener('load', () => {
    // Mostrar burbuja bienvenida
    const bubble = document.getElementById('chat-bubble');
    bubble.style.display = 'block';
    setTimeout(() => bubble.style.display = 'none', 7000);
});
