document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');
    const toggleIcon = document.getElementById('toggleIcon');

    if (togglePassword && passwordInput && toggleIcon) {
        togglePassword.addEventListener('click', function() {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            const type = isPassword ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            toggleIcon.classList.toggle('fa-eye', !isPassword);
            toggleIcon.classList.toggle('fa-eye-slash', isPassword);

            // Fallback for when Font Awesome fails to load
            togglePassword.setAttribute('title', isPassword ? 'Hide password' : 'Show password');
        });
    }
    
    const loginForm = document.getElementById('loginForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const usernameInput = loginForm.querySelector('input[name="username"]');
    const submitBtn = loginForm.querySelector('.btn-login');

    function validateField(input) {
        const isEmpty = input.value.trim() === '';
        input.classList.toggle('input-invalid', isEmpty);
        input.classList.toggle('input-valid', !isEmpty);
        return !isEmpty;
    }

    [usernameInput, passwordInput].forEach(input => {
        input.addEventListener('blur', () => validateField(input));
        input.addEventListener('input', () => input.classList.remove('input-invalid'));
    });

    loginForm.addEventListener('submit', function(e) {
        const usernameValid = validateField(usernameInput);
        const passwordValid = validateField(passwordInput);

        if (!usernameValid || !passwordValid) {
            e.preventDefault();
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Logging in...';
        loadingOverlay.classList.add('active');
    });
    
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.remove();
        }, 5000);
    });
});
