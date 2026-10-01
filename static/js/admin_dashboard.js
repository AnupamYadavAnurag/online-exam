/**
 * Admin Dashboard Management JavaScript
 */

let activeTab = 'overview';
let currentExamForQuestions = null;

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Validate Admin Session
    const userRes = await API.request('/api/auth/me');
    if (!userRes.ok || !userRes.data.user || userRes.data.user.role !== 'admin') {
        window.location.href = '/login';
        return;
    }

    document.getElementById('admin-display-name').textContent = `Admin: ${userRes.data.user.full_name}`;

    // 2. Setup Navigation
    setupTabNavigation();

    // 3. Load Initial Overview
    loadOverviewStats();
    loadDepartments();

    // 4. Setup Form Event Listeners
    setupFormListeners();
});

function setupTabNavigation() {
    const navItems = document.querySelectorAll('.nav-tab');
    navItems.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = tab.dataset.tab;
            switchTab(targetTab);
        });
    });

    document.getElementById('logout-btn').addEventListener('click', async () => {
        await API.request('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    });
}

function switchTab(tabName) {
    activeTab = tabName;
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

    const selectedNav = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
    if (selectedNav) selectedNav.classList.add('active');

    const selectedContent = document.getElementById(`tab-${tabName}`);
    if (selectedContent) selectedContent.style.display = 'block';

    if (tabName === 'overview') loadOverviewStats();
    else if (tabName === 'students') loadStudentsTable();
    else if (tabName === 'courses') loadCoursesTable();
    else if (tabName === 'exams') loadExamsTable();
    else if (tabName === 'results') loadResultsTable();
}

// --- Results Management ---
async function loadResultsTable() {
    const tbody = document.getElementById('results-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px;">Loading student results...</td></tr>';

    const res = await API.request('/api/admin/results');
    if (res.ok && res.data.results) {
        tbody.innerHTML = '';
        if (res.data.results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px;">No exam results recorded yet.</td></tr>';
            return;
        }

        res.data.results.forEach(r => {
            const tr = document.createElement('tr');
            const statusBadge = r.status === 'PASS'
                ? `<span class="badge badge-success">PASS</span>`
                : `<span class="badge badge-danger">FAIL</span>`;

            tr.innerHTML = `
                <td><strong>${escapeHtml(r.student_name)}</strong><br><small style="color:#94a3b8;">${r.student_id || ''}</small></td>
                <td>${escapeHtml(r.exam_title)}<br><small style="color:#818cf8;">${r.course_code}</small></td>
                <td><strong>${r.score} / ${r.total_possible_score}</strong></td>
                <td>${r.percentage}%</td>
                <td>${statusBadge}</td>
                <td>${r.submit_time || 'N/A'}</td>
                <td>
                    <button class="btn-sm btn-warning" id="btn-reset-result-${r.id}" onclick="deleteResult(${r.id})">Reset Attempt</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

async function deleteResult(resultId) {
    if (!confirm('Resetting this result will allow the student to re-attempt the exam. Proceed?')) return;
    const res = await API.request(`/api/admin/results/${resultId}`, { method: 'DELETE' });
    if (res.ok) loadResultsTable();
    else alert(res.data.message || 'Failed to reset result.');
}

// --- Overview Stats ---
async function loadOverviewStats() {
    const res = await API.request('/api/admin/stats');
    if (res.ok && res.data.stats) {
        document.getElementById('stat-students').textContent = res.data.stats.students;
        document.getElementById('stat-blocked').textContent = res.data.stats.blocked_students;
        document.getElementById('stat-courses').textContent = res.data.stats.courses;
        document.getElementById('stat-exams').textContent = res.data.stats.exams;
        document.getElementById('stat-published').textContent = res.data.stats.published_exams;
    }
}

// --- Load Departments Dropdown ---
let globalDepartments = [];
async function loadDepartments() {
    const res = await API.request('/api/admin/departments');
    if (res.ok && res.data.departments) {
        globalDepartments = res.data.departments;
        const courseDeptSelect = document.getElementById('course-dept');
        if (courseDeptSelect) {
            courseDeptSelect.innerHTML = '<option value="">Select Department...</option>';
            globalDepartments.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d.id;
                opt.textContent = `${d.dept_code} - ${d.dept_name}`;
                courseDeptSelect.appendChild(opt);
            });
        }
    }
}

// --- Students Management ---
async function loadStudentsTable() {
    const tbody = document.getElementById('students-table-body');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px;">Loading students data...</td></tr>';

    const res = await API.request('/api/admin/students');
    if (res.ok && res.data.students) {
        tbody.innerHTML = '';
        if (res.data.students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px;">No registered students found.</td></tr>';
            return;
        }

        res.data.students.forEach(s => {
            const tr = document.createElement('tr');
            const statusBadge = s.status === 'blocked'
                ? `<span class="badge badge-danger" id="status-student-${s.id}">Blocked</span>`
                : `<span class="badge badge-success" id="status-student-${s.id}">Active</span>`;

            const toggleBtnText = s.status === 'blocked' ? 'Unblock' : 'Block';
            const toggleBtnClass = s.status === 'blocked' ? 'btn-sm btn-success' : 'btn-sm btn-warning';
            const targetActionStatus = s.status === 'blocked' ? 'active' : 'blocked';

            tr.innerHTML = `
                <td><strong>${s.student_id || 'N/A'}</strong></td>
                <td>${s.full_name}<br><small style="color:#94a3b8;">${s.username}</small></td>
                <td>${s.email}<br><small style="color:#94a3b8;">${s.phone}</small></td>
                <td>${s.course_code || 'Unassigned'}</td>
                <td>${statusBadge}</td>
                <td>${s.dob}</td>
                <td>
                    <button class="${toggleBtnClass}" id="btn-toggle-student-${s.id}" onclick="toggleStudentStatus(${s.id}, '${targetActionStatus}')">${toggleBtnText}</button>
                    <button class="btn-sm btn-danger" id="btn-delete-student-${s.id}" onclick="deleteStudent(${s.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

async function toggleStudentStatus(studentId, newStatus) {
    const res = await API.request(`/api/admin/students/${studentId}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus })
    });
    if (res.ok) {
        loadStudentsTable();
        loadOverviewStats();
    } else {
        alert(res.data.message || 'Failed to update status.');
    }
}

async function deleteStudent(studentId) {
    if (!confirm('Are you sure you want to delete this student account? All exam history will be removed.')) return;
    const res = await API.request(`/api/admin/students/${studentId}`, { method: 'DELETE' });
    if (res.ok) {
        loadStudentsTable();
        loadOverviewStats();
    } else {
        alert(res.data.message || 'Failed to delete student.');
    }
}

// --- Course Management ---
async function loadCoursesTable() {
    const tbody = document.getElementById('courses-table-body');
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px;">Loading courses...</td></tr>';

    const res = await API.request('/api/admin/courses');
    if (res.ok && res.data.courses) {
        tbody.innerHTML = '';
        res.data.courses.forEach(c => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${c.course_code}</strong></td>
                <td>${c.course_name}</td>
                <td>${c.dept_name}</td>
                <td><span class="badge badge-info">${c.total_exams} Exams</span></td>
                <td>
                    <button class="btn-sm btn-danger" id="btn-delete-course-${c.id}" onclick="deleteCourse(${c.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Also update exam course select dropdown
        const examCourseSelect = document.getElementById('exam-course');
        if (examCourseSelect) {
            examCourseSelect.innerHTML = '<option value="">Select Course...</option>';
            res.data.courses.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = `${c.course_code} - ${c.course_name}`;
                examCourseSelect.appendChild(opt);
            });
        }
    }
}

async function deleteCourse(courseId) {
    if (!confirm('Deleting this course will delete all associated exams and questions. Proceed?')) return;
    const res = await API.request(`/api/admin/courses/${courseId}`, { method: 'DELETE' });
    if (res.ok) loadCoursesTable();
    else alert(res.data.message || 'Failed to delete course.');
}

// --- Exam Management ---
async function loadExamsTable() {
    const tbody = document.getElementById('exams-table-body');
    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px;">Loading exams...</td></tr>';

    const res = await API.request('/api/admin/exams');
    if (res.ok && res.data.exams) {
        tbody.innerHTML = '';
        res.data.exams.forEach(e => {
            const tr = document.createElement('tr');
            const isPublished = e.is_published === 1;
            const publishBadge = isPublished
                ? `<span class="badge badge-success" id="publish-status-${e.id}">Published</span>`
                : `<span class="badge badge-warning" id="publish-status-${e.id}">Draft (Unpublished)</span>`;

            const toggleBtnText = isPublished ? 'Unpublish' : 'Publish';
            const toggleBtnClass = isPublished ? 'btn-sm btn-warning' : 'btn-sm btn-success';

            tr.innerHTML = `
                <td><strong>${e.title}</strong><br><small style="color:#94a3b8;">${e.description || ''}</small></td>
                <td>${e.course_code}</td>
                <td>${e.duration_minutes} Mins</td>
                <td>${e.total_marks} Marks</td>
                <td><span class="badge badge-info" id="exam-qcount-${e.id}">${e.question_count} MCQs</span></td>
                <td>${publishBadge}</td>
                <td>
                    <button class="${toggleBtnClass}" id="btn-toggle-publish-${e.id}" onclick="toggleExamPublish(${e.id}, ${!isPublished})">${toggleBtnText}</button>
                    <button class="btn-sm btn-primary" id="btn-manage-questions-${e.id}" onclick="openQuestionsModal(${e.id}, '${escapeHtml(e.title)}')">Questions</button>
                    <button class="btn-sm btn-danger" id="btn-delete-exam-${e.id}" onclick="deleteExam(${e.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

async function toggleExamPublish(examId, setPublished) {
    const res = await API.request(`/api/admin/exams/${examId}/publish`, {
        method: 'PUT',
        body: JSON.stringify({ is_published: setPublished })
    });
    if (res.ok) loadExamsTable();
    else alert(res.data.message || 'Failed to toggle publish status.');
}

async function deleteExam(examId) {
    if (!confirm('Are you sure you want to delete this exam and all its questions?')) return;
    const res = await API.request(`/api/admin/exams/${examId}`, { method: 'DELETE' });
    if (res.ok) loadExamsTable();
    else alert(res.data.message || 'Failed to delete exam.');
}

// --- Question Management Modal ---
async function openQuestionsModal(examId, examTitle) {
    currentExamForQuestions = examId;
    document.getElementById('modal-exam-title').textContent = examTitle;
    document.getElementById('questions-modal').style.display = 'flex';
    loadExamQuestions(examId);
}

function closeQuestionsModal() {
    document.getElementById('questions-modal').style.display = 'none';
    currentExamForQuestions = null;
    loadExamsTable();
}

async function loadExamQuestions(examId) {
    const container = document.getElementById('questions-list-container');
    container.innerHTML = '<p style="text-align:center; padding:15px; color:#94a3b8;">Loading questions...</p>';

    const res = await API.request(`/api/admin/exams/${examId}/questions`);
    if (res.ok && res.data.questions) {
        container.innerHTML = '';
        if (res.data.questions.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding:15px; color:#94a3b8;">No questions added yet. Add your first MCQ below.</p>';
            return;
        }

        res.data.questions.forEach((q, idx) => {
            const card = document.createElement('div');
            card.className = 'question-card';
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                    <strong style="color:#f8fafc;">Q${idx + 1}. ${escapeHtml(q.question_text)}</strong>
                    <div>
                        <span class="badge badge-info">${q.marks} Mark(s)</span>
                        <button class="btn-sm btn-danger" id="btn-delete-q-${q.id}" onclick="deleteQuestion(${q.id})">Delete</button>
                    </div>
                </div>
                <div class="options-grid">
                    <div class="opt-box ${q.correct_option === 'A' ? 'correct' : ''}">A: ${escapeHtml(q.option_a)}</div>
                    <div class="opt-box ${q.correct_option === 'B' ? 'correct' : ''}">B: ${escapeHtml(q.option_b)}</div>
                    <div class="opt-box ${q.correct_option === 'C' ? 'correct' : ''}">C: ${escapeHtml(q.option_c)}</div>
                    <div class="opt-box ${q.correct_option === 'D' ? 'correct' : ''}">D: ${escapeHtml(q.option_d)}</div>
                </div>
            `;
            container.appendChild(card);
        });
    }
}

async function deleteQuestion(qId) {
    if (!confirm('Delete this question?')) return;
    const res = await API.request(`/api/admin/questions/${qId}`, { method: 'DELETE' });
    if (res.ok && currentExamForQuestions) loadExamQuestions(currentExamForQuestions);
}

// --- Setup Form Submission Listeners ---
function setupFormListeners() {
    // 1. Create Course Form
    const courseForm = document.getElementById('add-course-form');
    if (courseForm) {
        courseForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const code = document.getElementById('course-code').value.trim();
            const name = document.getElementById('course-name').value.trim();
            const dept_id = document.getElementById('course-dept').value;
            const description = document.getElementById('course-desc').value.trim();
            const alertBox = document.getElementById('course-form-alert');

            const res = await API.request('/api/admin/courses', {
                method: 'POST',
                body: JSON.stringify({ course_code: code, course_name: name, dept_id, description })
            });

            if (res.ok) {
                alertBox.className = 'alert alert-success';
                alertBox.textContent = res.data.message;
                alertBox.style.display = 'block';
                courseForm.reset();
                loadCoursesTable();
            } else {
                alertBox.className = 'alert alert-danger';
                alertBox.textContent = res.data.message || 'Course creation failed.';
                alertBox.style.display = 'block';
            }
        });
    }

    // 2. Create Exam Form
    const examForm = document.getElementById('create-exam-form');
    if (examForm) {
        examForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            API.clearErrors(examForm);

            const title = document.getElementById('exam-title').value.trim();
            const course_id = document.getElementById('exam-course').value;
            const duration_minutes = document.getElementById('exam-duration').value;
            const total_marks = document.getElementById('exam-marks').value;
            const description = document.getElementById('exam-desc').value.trim();
            const alertBox = document.getElementById('exam-form-alert');

            const res = await API.request('/api/admin/exams', {
                method: 'POST',
                body: JSON.stringify({ title, course_id, duration_minutes, total_marks, description })
            });

            if (res.ok) {
                alertBox.className = 'alert alert-success';
                alertBox.textContent = res.data.message;
                alertBox.style.display = 'block';
                examForm.reset();
                loadExamsTable();
            } else {
                if (res.data.errors) API.showErrors(res.data.errors);
                alertBox.className = 'alert alert-danger';
                alertBox.textContent = res.data.message || 'Exam creation failed.';
                alertBox.style.display = 'block';
            }
        });
    }

    // 3. Add Question Form
    const qForm = document.getElementById('add-question-form');
    if (qForm) {
        qForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!currentExamForQuestions) return;

            const question_text = document.getElementById('q-text').value.trim();
            const option_a = document.getElementById('q-op-a').value.trim();
            const option_b = document.getElementById('q-op-b').value.trim();
            const option_c = document.getElementById('q-op-c').value.trim();
            const option_d = document.getElementById('q-op-d').value.trim();
            const correct_option = document.getElementById('q-correct').value;
            const alertBox = document.getElementById('q-form-alert');

            const res = await API.request(`/api/admin/exams/${currentExamForQuestions}/questions`, {
                method: 'POST',
                body: JSON.stringify({ question_text, option_a, option_b, option_c, option_d, correct_option, marks: 1 })
            });

            if (res.ok) {
                alertBox.className = 'alert alert-success';
                alertBox.textContent = 'Question added successfully!';
                alertBox.style.display = 'block';
                qForm.reset();
                loadExamQuestions(currentExamForQuestions);
            } else {
                alertBox.className = 'alert alert-danger';
                alertBox.textContent = res.data.message || 'Failed to add question.';
                alertBox.style.display = 'block';
            }
        });
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
