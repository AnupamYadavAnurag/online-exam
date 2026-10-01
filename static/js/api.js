/**
 * API Helper Utility for Online Examination System
 */
const API = {
    async request(url, options = {}) {
        const defaultHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };

        options.headers = { ...defaultHeaders, ...options.headers };

        try {
            const response = await fetch(url, options);
            const data = await response.json();
            return { ok: response.ok, status: response.status, data };
        } catch (error) {
            console.error('API Error:', error);
            return { ok: false, status: 500, data: { status: 'error', message: 'Network or server error.' } };
        }
    },

    clearErrors(formElement) {
        if (!formElement) return;
        const errors = formElement.querySelectorAll('.field-error');
        errors.forEach(el => el.textContent = '');

        const alerts = formElement.querySelectorAll('.alert');
        alerts.forEach(el => {
            el.style.display = 'none';
            el.textContent = '';
        });
    },

    showErrors(errorsDict, globalErrorElement = null) {
        if (typeof errorsDict === 'object') {
            for (const [key, msg] of Object.entries(errorsDict)) {
                const errElement = document.getElementById(`err-${key}`);
                if (errElement) {
                    errElement.textContent = msg;
                }
            }
        }
        if (globalErrorElement && errorsDict.global) {
            globalErrorElement.textContent = errorsDict.global;
            globalErrorElement.style.display = 'block';
        }
    }
};
