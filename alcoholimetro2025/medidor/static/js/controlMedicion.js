
// Mostrar mensaje de consola al cargar el JS
console.log("controlMedicion.js cargado correctamente");

// Obtener token CSRF de cookies
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
    return cookieValue ? cookieValue.split('=')[1] : '';
}

// Mostrar notificación (estilo Bootstrap)
function mostrarNotificacion(mensaje, tipo = 'info') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} mt-3`;
    alerta.textContent = mensaje;

    const contenedor = document.querySelector('.container');
    contenedor.prepend(alerta);

    setTimeout(() => alerta.remove(), 4000);
}

// Cambiar visualmente estado de medición
function actualizarEstado(activa) {
    const estado = document.getElementById('estadoMedicion');
    const btnIniciar = document.getElementById('btnIniciar');
    const btnDetener = document.getElementById('btnDetener');

    if (activa) {
        estado.className = "alert alert-success mb-4";
        estado.textContent = "Estado: Activa";
        btnIniciar.classList.add('disabled');
        btnDetener.classList.remove('disabled');
    } else {
        estado.className = "alert alert-secondary mb-4";
        estado.textContent = "Estado: Inactiva";
        btnIniciar.classList.remove('disabled');
        btnDetener.classList.add('disabled');
    }
}

// Función principal para controlar la medición
async function controlarMedicion(action) {
    const btn = action === 'iniciar' ? btnIniciar : btnDetener;
    btn.disabled = true;

    try {
        const response = await fetch('/control-medicion/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `action=${action}`
        });

        const data = await response.json();
        console.log('Respuesta del servidor:', data);

        if (data.warning) {
            mostrarNotificacion(`Advertencia: ${data.warning}`, 'warning');
        } else {
            mostrarNotificacion(data.status, 'success');
        }

        actualizarEstado(action === 'iniciar');

    } catch (error) {
        console.error('Error en la solicitud:', error);
        mostrarNotificacion('Error al comunicarse con el servidor', 'danger');
    } finally {
        btn.disabled = false;
    }
}

// Conectar botones al cargar el DOM
document.addEventListener('DOMContentLoaded', function () {
    window.btnIniciar = document.getElementById('btnIniciar');
    window.btnDetener = document.getElementById('btnDetener');

    if (btnIniciar) {
        btnIniciar.addEventListener('click', () => controlarMedicion('iniciar'));
    }
    if (btnDetener) {
        btnDetener.addEventListener('click', () => controlarMedicion('detener'));
    }

    console.log("Botones conectados correctamente");
});
