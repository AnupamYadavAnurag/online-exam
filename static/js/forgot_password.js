document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('forgot-form');
    const msgAlert = document.getElementById('forgot-msg');
    const demoBox = document.getElementById('demo-token-display');
    const forgotBtn = document.getElementById('forgot-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        API.clearErrors(form);

        const email = document.getElementById('forgot-email').value.trim();
        if (!email) {
            API.showErrors({ email: 'Email address is required.' });
            msgAlert.className = 'alert alert-danger';
            msgAlert.textContent = 'Please enter your email address.';
            msgAlert.style.display = 'block';
            return;
        }

        forgotBtn.disabled = true;
        forgotBtn.textContent = 'Sending...';

        const res = await API.request('/api/auth/forgot-password', {
            method: 'POST',
            body: JSON.stringify({ email })
        });

        forgotBtn.disabled = false;
        forgotBtn.textContent = 'Send Reset Link';

        if (res.ok) {
            msgAlert.className = 'alert alert-success';
            msgAlert.textContent = res.data.message;
            msgAlert.style.display = 'block';

            if (res.data.demo_reset_url) {
                demoBox.innerHTML = `
                    <div style="background: rgba(99, 102, 241, 0.2); border: 1px dashed #818cf8; padding: 14px; border-radius: 8px; margin-top: 15px; text-align: left;">
                        <strong style="color: #a5b4fc; display: block; margin-bottom: 6px;">🛠️ DEMO MODE - RESET LINK:</strong>
                        <p style="font-size: 12px; word-break: break-all; margin-bottom: 10px;">Token: <code>${res.data.demo_reset_token}</code></p>
                        <a href="${res.data.demo_reset_url}" id="demo-reset-link" class="btn-primary" style="display: inline-block; padding: 8px 16px; font-size: 13px; text-decoration: none; text-align: center;">Click to Reset Password</a>
                    </div>
                `;
                demoBox.style.display = 'block';
            }
        } else {
            msgAlert.className = 'alert alert-danger';
            msgAlert.textContent = res.data.message || 'Failed to process request.';
            msgAlert.style.display = 'block';
        }
    });
});
