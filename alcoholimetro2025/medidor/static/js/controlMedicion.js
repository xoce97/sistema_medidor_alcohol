document.addEventListener('DOMContentLoaded', function() {
    const btnIniciar = document.getElementById('btnIniciar');
    const btnDetener = document.getElementById('btnDetener');
    const estado = document.querySelector('#estado .badge');

    // Función para actualizar la UI
    function actualizarEstado(activa) {
        btnIniciar.disabled = activa;
        btnDetener.disabled = !activa;
        estado.className = activa ? 'badge bg-success' : 'badge bg-secondary';
        estado.textContent = activa ? 'Activo' : 'Inactivo';
    }

    // Manejadores de eventos
    btnIniciar.addEventListener('click', () => {
        controlarMedicion('iniciar');
    });

    btnDetener.addEventListener('click', () => {
        controlarMedicion('detener');
    });

    // Función para enviar peticiones al servidor
    function controlarMedicion(accion) {
        fetch('/control-medicion/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `action=${accion}`
        })
        .then(response => response.json())
        .then(data => actualizarEstado(data.activa))
        .catch(error => console.error('Error:', error));
    }

    // Función para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Verificar estado al cargar la página
    fetch('/estado-medicion/')
        .then(response => response.json())
        .then(data => actualizarEstado(data.activa))
        .catch(error => console.error('Error:', error));
});