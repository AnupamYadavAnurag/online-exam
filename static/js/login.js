document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('login-form');
    const errorAlert = document.getElementById('login-error');
    const successAlert = document.getElementById('login-success');
    const loginBtn = document.getElementById('login-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        API.clearErrors(form);

        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        const remember_me = document.getElementById('login-remember').checked;

        let errors = {};
        if (!username) errors.username = "Username or Email is required.";
        if (!password) errors.password = "Password is required.";

        if (Object.keys(errors).length > 0) {
            API.showErrors(errors);
            errorAlert.textContent = "Please fill in all required fields.";
            errorAlert.style.display = 'block';
            return;
        }

        loginBtn.disabled = true;
        loginBtn.textContent = 'Authenticating...';

        const res = await API.request('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password, remember_me })
        });

        loginBtn.disabled = false;
        loginBtn.textContent = 'Sign In';

        if (res.ok) {
            successAlert.textContent = res.data.message || 'Login successful! Redirecting...';
            successAlert.style.display = 'block';
            setTimeout(() => {
                if (res.data.user && res.data.user.role === 'admin') {
                    window.location.href = '/admin-dashboard';
                } else {
                    window.location.href = '/student-dashboard';
                }
            }, 1000);
        } else {
            if (res.data.errors) {
                API.showErrors(res.data.errors);
            }
            errorAlert.textContent = res.data.message || 'Invalid credentials.';
            errorAlert.style.display = 'block';
        }
    });
});
