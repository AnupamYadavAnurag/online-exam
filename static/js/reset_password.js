document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('reset-form');
    const msgAlert = document.getElementById('reset-msg');
    const resetBtn = document.getElementById('reset-btn');

    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');

    if (!token) {
        msgAlert.className = 'alert alert-danger';
        msgAlert.textContent = 'Invalid or missing reset token in URL.';
        msgAlert.style.display = 'block';
        resetBtn.disabled = true;
        return;
    }

    // Verify token validity
    const verifyRes = await API.request(`/api/auth/verify-token/${token}`);
    if (!verifyRes.ok) {
        msgAlert.className = 'alert alert-danger';
        msgAlert.textContent = verifyRes.data.message || 'Reset token expired or invalid.';
        msgAlert.style.display = 'block';
        resetBtn.disabled = true;
        return;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        API.clearErrors(form);

        const password = document.getElementById('reset-password').value;
        const confirm_password = document.getElementById('reset-confirm').value;

        let errors = {};
        if (!password) errors.password = "Password is required.";
        else if (password.length < 8 || password.length > 20) errors.password = "Password must be between 8 and 20 characters.";

        if (!confirm_password) errors.confirm_password = "Confirm password is required.";
        else if (password !== confirm_password) errors.confirm_password = "Passwords do not match.";

        if (Object.keys(errors).length > 0) {
            API.showErrors(errors);
            msgAlert.className = 'alert alert-danger';
            msgAlert.textContent = 'Please fix the password errors.';
            msgAlert.style.display = 'block';
            return;
        }

        resetBtn.disabled = true;
        resetBtn.textContent = 'Resetting Password...';

        const res = await API.request('/api/auth/reset-password', {
            method: 'POST',
            body: JSON.stringify({ token, password, confirm_password })
        });

        resetBtn.disabled = false;
        resetBtn.textContent = 'Reset Password';

        if (res.ok) {
            msgAlert.className = 'alert alert-success';
            msgAlert.textContent = res.data.message || 'Password reset successful! Redirecting to login...';
            msgAlert.style.display = 'block';
            form.reset();
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            if (res.data.errors) {
                API.showErrors(res.data.errors);
            }
            msgAlert.className = 'alert alert-danger';
            msgAlert.textContent = res.data.message || 'Password reset failed.';
            msgAlert.style.display = 'block';
        }
    });
});
