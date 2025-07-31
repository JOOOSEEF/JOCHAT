function loadMessages() {
    fetch('/mensajes')
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
        body: JSON.stringify({ usuario: "Cliente", texto: text })
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

// Cargar mensajes cada 3 segundos
loadMessages();
setInterval(loadMessages, 3000);
