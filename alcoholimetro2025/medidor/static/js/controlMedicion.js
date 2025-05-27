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
        console.log('Respuesta:', data);
        
        if (data.warning) {
            mostrarNotificacion(`Advertencia: ${data.warning}`, 'warning');
        } else {
            mostrarNotificacion(data.status, 'success');
        }
        
        actualizarEstado(action === 'iniciar');
        
    } catch (error) {
        console.error('Error:', error);
        mostrarNotificacion('Error al comunicarse con el servidor', 'danger');
    } finally {
        btn.disabled = false;
    }
}