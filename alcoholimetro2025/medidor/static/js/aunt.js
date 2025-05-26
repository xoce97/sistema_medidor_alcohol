document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    
    if (!form) {
        console.error('Formulario no encontrado');
        return;
    }

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Obtener campos
        const username = form.querySelector('[name="username"]').value.trim();
        const password = form.querySelector('[name="password"]').value.trim();
        const errorDiv = document.getElementById('loginError');

        // Validación
        if (!username || !password) {
            showError(errorDiv, '¡Todos los campos son obligatorios!');
            return;
        }

        if (username.includes(' ') || password.includes(' ')) {
            showError(errorDiv, '¡No se permiten espacios en blanco!');
            return;
        }

        // Si pasa la validación, enviar el formulario
        form.submit();
    });

    function showError(element, message) {
        if (element) {
            element.textContent = message;
            element.style.display = 'block';
        }
    }
});