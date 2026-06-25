document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');
    const toggleIcon = document.getElementById('toggleIcon');

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        if (type === 'text') {
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        } else {
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        }
    });
    
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
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});
