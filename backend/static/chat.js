// Generar cliente_id si no existe
if (!localStorage.getItem('cliente_id')) {
    localStorage.setItem('cliente_id', 'cliente_' + Math.random().toString(36).substring(2, 10));
}
const cliente_id = localStorage.getItem('cliente_id');

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

// Enviar bienvenida automáticamente si aún no se ha hecho
function enviarBienvenida() {
    const key = `bienvenida_enviada_${cliente_id}`;
    if (!localStorage.getItem(key)) {
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
            localStorage.setItem(key, 'true');
            loadMessages();
        })
        .catch(err => {
            console.error('Error al enviar mensaje de bienvenida:', err);
        });
    } else {
        loadMessages();
    }
}

// Ejecutar
enviarBienvenida();
setInterval(loadMessages, 3000);
