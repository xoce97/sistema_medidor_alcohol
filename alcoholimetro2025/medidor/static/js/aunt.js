document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const errorDiv = document.getElementById('loginError');

    if (!form) return;

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        errorDiv.style.display = 'none';
        
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                window.location.href = '/index/';  // Redirigir al index
            } else {
                const errors = await response.json();
                showError(errorDiv, Object.values(errors).join(' '));
            }
        } catch (error) {
            showError(errorDiv, 'Error de conexión');
        }
    });

    function showError(element, message) {
        element.textContent = message;
        element.style.display = 'block';
    }
});