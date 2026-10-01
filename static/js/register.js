document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('register-form');
    const courseSelect = document.getElementById('register-course');
    const errorAlert = document.getElementById('register-error');
    const successAlert = document.getElementById('register-success');
    const registerBtn = document.getElementById('register-btn');

    // 1. Fetch courses for dropdown
    try {
        const res = await API.request('/api/auth/courses');
        if (res.ok && res.data.courses) {
            courseSelect.innerHTML = '<option value="">Select your course...</option>';
            res.data.courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = `${c.course_code} - ${c.course_name}`;
                courseSelect.appendChild(opt);
            });
        }
    } catch (err) {
        console.error('Failed to load courses:', err);
    }

    // 2. Handle Form Submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        API.clearErrors(form);

        const formData = {
            full_name: document.getElementById('register-fullname').value.trim(),
            student_id: document.getElementById('register-studentid').value.trim(),
            email: document.getElementById('register-email').value.trim(),
            phone: document.getElementById('register-phone').value.trim(),
            username: document.getElementById('register-username').value.trim(),
            password: document.getElementById('register-password').value,
            confirm_password: document.getElementById('register-confirm-password').value,
            course_id: courseSelect.value,
            dob: document.getElementById('register-dob').value
        };

        // Client-side quick checks
        let clientErrors = {};
        if (!formData.full_name) clientErrors.full_name = "Full Name is required.";
        if (!formData.student_id) clientErrors.student_id = "Student ID is required.";
        if (!formData.email) clientErrors.email = "Email is required.";
        if (!formData.phone) clientErrors.phone = "Phone number is required.";
        if (!formData.username) clientErrors.username = "Username is required.";
        if (!formData.password) clientErrors.password = "Password is required.";
        if (!formData.confirm_password) clientErrors.confirm_password = "Confirm Password is required.";
        if (formData.password && formData.confirm_password && formData.password !== formData.confirm_password) {
            clientErrors.confirm_password = "Passwords do not match.";
        }
        if (!formData.course_id) clientErrors.course_id = "Please select a course.";
        if (!formData.dob) clientErrors.dob = "Date of Birth is required.";

        if (Object.keys(clientErrors).length > 0) {
            API.showErrors(clientErrors);
            errorAlert.textContent = "Please fix the validation errors below.";
            errorAlert.style.display = 'block';
            return;
        }

        registerBtn.disabled = true;
        registerBtn.textContent = 'Registering...';

        const res = await API.request('/api/auth/register', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        registerBtn.disabled = false;
        registerBtn.textContent = 'Create Account';

        if (res.ok) {
            successAlert.textContent = res.data.message || 'Registration successful! Redirecting to login...';
            successAlert.style.display = 'block';
            form.reset();
            setTimeout(() => {
                window.location.href = '/login';
            }, 1800);
        } else {
            if (res.data.errors) {
                API.showErrors(res.data.errors);
            }
            errorAlert.textContent = res.data.message || 'Registration failed. Please check your details.';
            errorAlert.style.display = 'block';
        }
    });
});
