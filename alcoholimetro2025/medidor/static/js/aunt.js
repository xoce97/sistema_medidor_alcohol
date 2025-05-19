// Validación de formulario de login
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('login-form');
    
    form.addEventListener('submit', function(e) {
        const username = form.querySelector('[name="username"]').value;
        const password = form.querySelector('[name="password"]').value;
        
        if (!username || !password) {
            e.preventDefault();
            alert('Por favor complete todos los campos');
        }
    });
});