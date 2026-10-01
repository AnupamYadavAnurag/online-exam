/**
 * Student Portal & Examination JavaScript
 */

let activeExamSession = null; // Holds { result_id, exam, questions, answers, timerInterval, timeRemaining }

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verify Student Session
    const userRes = await API.request('/api/auth/me');
    if (!userRes.ok || !userRes.data.user || userRes.data.user.role !== 'student') {
        window.location.href = '/login';
        return;
    }

    document.getElementById('user-display-name').textContent = `Student: ${userRes.data.user.full_name}`;

    // 2. Setup Navigation
    setupStudentNavigation();

    // 3. Load Initial Data
    loadAvailableExams();
    loadStudentProfile();
});

function setupStudentNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(tab.dataset.tab);
        });
    });

    document.getElementById('logout-btn').addEventListener('click', async () => {
        await API.request('/api/auth/logout', { method: 'POST' });
        window.location.href = '/login';
    });
}

function switchTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

    const selectedTab = document.querySelector(`.nav-tab[data-tab="${tabName}"]`);
    if (selectedTab) selectedTab.classList.add('active');

    const selectedContent = document.getElementById(`tab-${tabName}`);
    if (selectedContent) selectedContent.style.display = 'block';

    if (tabName === 'exams') loadAvailableExams();
    else if (tabName === 'profile') loadStudentProfile();
}

// --- Profile ---
async function loadStudentProfile() {
    const res = await API.request('/api/student/profile');
    if (res.ok && res.data.profile) {
        const p = res.data.profile;
        document.getElementById('profile-fullname').textContent = p.full_name || 'N/A';
        document.getElementById('profile-studentid').textContent = p.student_id || 'N/A';
        document.getElementById('profile-email').textContent = p.email || 'N/A';
        document.getElementById('profile-phone').textContent = p.phone || 'N/A';
        document.getElementById('profile-username').textContent = p.username || 'N/A';
        document.getElementById('profile-course').textContent = p.course_name ? `${p.course_code} - ${p.course_name}` : 'Unassigned';
        document.getElementById('profile-dept').textContent = p.dept_name || 'N/A';
        document.getElementById('profile-dob').textContent = p.dob || 'N/A';
    }
}

// --- Available Exams Catalog ---
async function loadAvailableExams() {
    const container = document.getElementById('exams-catalog-container');
    container.innerHTML = '<p style="color:#94a3b8; text-align:center; padding: 20px;">Loading published exams catalog...</p>';

    const res = await API.request('/api/student/exams');
    if (res.ok && res.data.exams) {
        container.innerHTML = '';
        if (res.data.exams.length === 0) {
            container.innerHTML = '<p style="color:#94a3b8; text-align:center; padding: 20px;">No published exams currently available for your course.</p>';
            return;
        }

        res.data.exams.forEach(ex => {
            const card = document.createElement('div');
            card.className = 'exam-card';

            const actionButton = ex.already_attempted
                ? `<button class="btn-primary" style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color:#6ee7b7; cursor:default;" disabled>Completed (${ex.score}/${ex.total_marks} - ${ex.attempt_status})</button>`
                : `<button class="btn-primary" id="btn-start-exam-${ex.id}" onclick="startExamSession(${ex.id})">Start Exam Now 🚀</button>`;

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 12px;">
                    <div>
                        <h3 style="color:#f8fafc; font-size:18px;">${escapeHtml(ex.title)}</h3>
                        <span style="color:#818cf8; font-size:13px; font-weight:500;">${ex.course_code} - ${ex.course_name}</span>
                    </div>
                    <span class="badge badge-info">${ex.question_count} Questions</span>
                </div>
                <p style="color:#94a3b8; font-size:13px; margin-bottom: 16px;">${escapeHtml(ex.description || 'No instructions provided.')}</p>
                <div style="display:flex; gap:20px; font-size:13px; color:#cbd5e1; margin-bottom: 20px;">
                    <div>⏱️ <strong>Duration:</strong> ${ex.duration_minutes} Mins</div>
                    <div>🎯 <strong>Total Marks:</strong> ${ex.total_marks}</div>
                    <div>📈 <strong>Pass Mark:</strong> ${ex.pass_percentage}%</div>
                </div>
                ${actionButton}
            `;
            container.appendChild(card);
        });
    }
}

// --- Start Exam Session ---
async function startExamSession(examId) {
    const res = await API.request(`/api/student/exams/${examId}/start`, { method: 'POST' });
    if (!res.ok) {
        alert(res.data.message || 'Unable to start exam.');
        return;
    }

    const { result_id, exam, questions } = res.data;

    activeExamSession = {
        result_id,
        exam,
        questions,
        answers: {},
        timeRemaining: exam.duration_minutes * 60,
        timerInterval: null
    };

    renderExamTakingUI();
    startCountdownTimer();
}

function renderExamTakingUI() {
    const modal = document.getElementById('exam-session-modal');
    modal.style.display = 'flex';

    document.getElementById('active-exam-title').textContent = activeExamSession.exam.title;
    document.getElementById('active-exam-info').textContent = `Total Questions: ${activeExamSession.questions.length} | Marks: ${activeExamSession.exam.total_marks}`;

    const container = document.getElementById('exam-questions-form-container');
    container.innerHTML = '';

    activeExamSession.questions.forEach((q, idx) => {
        const qBox = document.createElement('div');
        qBox.className = 'exam-question-box';
        qBox.id = `q-container-${q.id}`;

        qBox.innerHTML = `
            <div style="font-weight:600; font-size:15px; color:#f8fafc; margin-bottom: 12px;">
                Q${idx + 1}. ${escapeHtml(q.question_text)} <span style="font-size:12px; color:#818cf8;">(${q.marks} Mark)</span>
            </div>
            <div class="mcq-options-list">
                <label class="mcq-option-item">
                    <input type="radio" name="q_${q.id}" id="q${q.id}-op-A" value="A" onchange="recordAnswer(${q.id}, 'A')">
                    <span><strong>A.</strong> ${escapeHtml(q.option_a)}</span>
                </label>
                <label class="mcq-option-item">
                    <input type="radio" name="q_${q.id}" id="q${q.id}-op-B" value="B" onchange="recordAnswer(${q.id}, 'B')">
                    <span><strong>B.</strong> ${escapeHtml(q.option_b)}</span>
                </label>
                <label class="mcq-option-item">
                    <input type="radio" name="q_${q.id}" id="q${q.id}-op-C" value="C" onchange="recordAnswer(${q.id}, 'C')">
                    <span><strong>C.</strong> ${escapeHtml(q.option_c)}</span>
                </label>
                <label class="mcq-option-item">
                    <input type="radio" name="q_${q.id}" id="q${q.id}-op-D" value="D" onchange="recordAnswer(${q.id}, 'D')">
                    <span><strong>D.</strong> ${escapeHtml(q.option_d)}</span>
                </label>
            </div>
        `;
        container.appendChild(qBox);
    });
}

function recordAnswer(questionId, optionValue) {
    if (activeExamSession) {
        activeExamSession.answers[questionId] = optionValue;
    }
}

// --- Live Countdown Timer ---
function startCountdownTimer() {
    const timerDisplay = document.getElementById('timer-display');
    
    updateTimerDisplay();

    activeExamSession.timerInterval = setInterval(() => {
        if (!activeExamSession) {
            clearInterval(activeExamSession.timerInterval);
            return;
        }

        activeExamSession.timeRemaining--;
        updateTimerDisplay();

        if (activeExamSession.timeRemaining <= 0) {
            clearInterval(activeExamSession.timerInterval);
            alert('⏱️ Exam Duration Expired! Auto-submitting your exam answers now...');
            submitExamSession(true); // Auto-submit on timeout
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerDisplay = document.getElementById('timer-display');
    if (!timerDisplay || !activeExamSession) return;

    const mins = Math.floor(activeExamSession.timeRemaining / 60);
    const secs = activeExamSession.timeRemaining % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

    timerDisplay.textContent = formatted;

    if (activeExamSession.timeRemaining < 60) {
        timerDisplay.style.color = '#ef4444'; // Red warning under 1 min
    } else {
        timerDisplay.style.color = '#38bdf8';
    }
}

// --- Submit Exam Session ---
async function submitExamSession(isAutoSubmit = false) {
    if (!activeExamSession) return;

    if (!isAutoSubmit) {
        const answeredCount = Object.keys(activeExamSession.answers).length;
        const totalCount = activeExamSession.questions.length;
        if (!confirm(`Are you sure you want to submit your exam?\n\nYou answered ${answeredCount} of ${totalCount} questions.`)) {
            return;
        }
    }

    if (activeExamSession.timerInterval) {
        clearInterval(activeExamSession.timerInterval);
    }

    const submitBtn = document.getElementById('btn-submit-exam');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Evaluating Exam...';
    }

    const res = await API.request(`/api/student/exams/${activeExamSession.exam.id}/submit`, {
        method: 'POST',
        body: JSON.stringify({
            result_id: activeExamSession.result_id,
            answers: activeExamSession.answers
        })
    });

    if (res.ok && res.data.result) {
        document.getElementById('exam-session-modal').style.display = 'none';
        showScoreCardModal(res.data.result.result_id);
        activeExamSession = null;
        loadAvailableExams();
    } else {
        alert(res.data.message || 'Failed to submit exam.');
        if (submitBtn) submitBtn.disabled = false;
    }
}

// --- Detailed Score Card Modal ---
async function showScoreCardModal(resultId) {
    const modal = document.getElementById('scorecard-modal');
    modal.style.display = 'flex';

    const res = await API.request(`/api/student/results/${resultId}`);
    if (res.ok && res.data.result) {
        const r = res.data.result;
        document.getElementById('card-exam-title').textContent = r.exam_title;
        document.getElementById('card-score').textContent = `${r.score} / ${r.total_possible_score}`;
        document.getElementById('card-percentage').textContent = `${r.percentage}%`;
        
        const statusBadge = document.getElementById('card-status');
        statusBadge.textContent = r.status;
        statusBadge.className = r.status === 'PASS' ? 'badge badge-success' : 'badge badge-danger';

        document.getElementById('card-correct').textContent = r.total_correct;
        document.getElementById('card-wrong').textContent = r.total_wrong;
        document.getElementById('card-unanswered').textContent = r.total_unanswered;

        // Render Answer Breakdown
        const breakdownContainer = document.getElementById('answer-breakdown-container');
        breakdownContainer.innerHTML = '';

        if (res.data.answers) {
            res.data.answers.forEach((ans, idx) => {
                const item = document.createElement('div');
                item.className = 'answer-review-item';
                const isCorrect = ans.is_correct === 1;
                const statusIcon = isCorrect ? '✅ Correct' : (ans.selected_option ? '❌ Incorrect' : '⚠️ Unanswered');
                const statusColor = isCorrect ? '#6ee7b7' : '#fca5a5';

                item.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <strong>Q${idx + 1}. ${escapeHtml(ans.question_text)}</strong>
                        <span style="color:${statusColor}; font-weight:600; font-size:12px;">${statusIcon}</span>
                    </div>
                    <div style="font-size:13px; color:#cbd5e1;">
                        Your Choice: <code>${ans.selected_option || 'None'}</code> | Correct Key: <strong style="color:#6ee7b7;">${ans.correct_option}</strong>
                    </div>
                `;
                breakdownContainer.appendChild(item);
            });
        }
    }
}

function closeScoreCardModal() {
    document.getElementById('scorecard-modal').style.display = 'none';
    loadAvailableExams();
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
