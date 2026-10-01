from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from middleware.auth_middleware import student_required
from db.connection import execute_query

student_bp = Blueprint("student", __name__)

@student_bp.route("/profile", methods=["GET"])
@student_required
def get_profile():
    """Returns profile details for currently logged-in student."""
    user_id = session["user"]["id"]
    query = """
        SELECT u.id, u.full_name, u.student_id, u.email, u.phone, u.username, u.dob,
               c.id as course_id, c.course_name, c.course_code, d.dept_name
        FROM users u
        LEFT JOIN courses c ON u.course_id = c.id
        LEFT JOIN departments d ON u.dept_id = d.id
        WHERE u.id = %s
    """
    profile = execute_query(query, (user_id,), fetchone=True)
    return jsonify({"status": "success", "profile": profile}), 200


@student_bp.route("/exams", methods=["GET"])
@student_required
def get_available_exams():
    """
    Returns list of published exams available to student.
    Includes attempt status (student can attempt an exam only once).
    """
    user_id = session["user"]["id"]
    
    # Get student's course_id
    user = execute_query("SELECT course_id FROM users WHERE id = %s", (user_id,), fetchone=True)
    student_course_id = user["course_id"] if user else None

    # Fetch only published exams
    query = """
        SELECT e.id, e.title, e.description, e.duration_minutes, e.total_marks, e.pass_percentage,
               c.course_name, c.course_code,
               (SELECT COUNT(*) FROM questions q WHERE q.exam_id = e.id) as question_count,
               r.id as result_id, r.score, r.percentage, r.status as attempt_status, r.is_submitted
        FROM exams e
        JOIN courses c ON e.course_id = c.id
        LEFT JOIN results r ON r.exam_id = e.id AND r.student_id = %s AND r.is_submitted = 1
        WHERE e.is_published = 1
        ORDER BY e.id DESC
    """
    exams = execute_query(query, (user_id,), fetchall=True) or []

    # Flag whether attempt is allowed
    processed_exams = []
    for ex in exams:
        ex["already_attempted"] = bool(ex["is_submitted"])
        processed_exams.append(ex)

    return jsonify({"status": "success", "exams": processed_exams}), 200


@student_bp.route("/exams/<int:exam_id>/start", methods=["POST"])
@student_required
def start_exam(exam_id):
    """
    Starts an exam for the student.
    Enforces Rule: A student can attempt an exam only once!
    """
    user_id = session["user"]["id"]

    # 1. Check if exam exists and is published
    exam = execute_query("SELECT * FROM exams WHERE id = %s AND is_published = 1", (exam_id,), fetchone=True)
    if not exam:
        return jsonify({"status": "error", "message": "Exam not found or not published."}), 404

    # 2. Enforce Single Attempt Rule
    existing_result = execute_query(
        "SELECT id, is_submitted FROM results WHERE student_id = %s AND exam_id = %s",
        (user_id, exam_id),
        fetchone=True
    )

    if existing_result and existing_result["is_submitted"] == 1:
        return jsonify({"status": "error", "message": "You have already attempted this exam. Multiple attempts are not allowed."}), 403

    # If there is an incomplete session, reuse it; otherwise create a new result row
    if existing_result and existing_result["is_submitted"] == 0:
        result_id = existing_result["id"]
    else:
        insert_query = """
            INSERT INTO results (student_id, exam_id, start_time, is_submitted)
            VALUES (%s, %s, NOW(), 0)
        """
        result_id = execute_query(insert_query, (user_id, exam_id), commit=True)

    # 3. Fetch questions (Excludes correct_option to prevent cheating)
    q_query = """
        SELECT id, question_text, option_a, option_b, option_c, option_d, marks, difficulty_level, topic
        FROM questions
        WHERE exam_id = %s
        ORDER BY id ASC
    """
    questions = execute_query(q_query, (exam_id,), fetchall=True) or []

    return jsonify({
        "status": "success",
        "result_id": result_id,
        "exam": {
            "id": exam["id"],
            "title": exam["title"],
            "description": exam["description"],
            "duration_minutes": exam["duration_minutes"],
            "total_marks": exam["total_marks"],
            "pass_percentage": float(exam["pass_percentage"])
        },
        "questions": questions
    }), 200


@student_bp.route("/exams/<int:exam_id>/submit", methods=["POST"])
@student_required
def submit_exam(exam_id):
    """
    Submits student exam answers and performs instant evaluation.
    Calculates score, percentage, Pass/Fail status, and breakdown.
    """
    user_id = session["user"]["id"]
    data = request.get_json() or {}
    result_id = data.get("result_id")
    user_answers = data.get("answers", {}) # Dict mapping question_id (str) -> selected_option ('A'/'B'/'C'/'D')

    if not result_id:
        return jsonify({"status": "error", "message": "Result session ID is required."}), 400

    # 1. Verify result record belongs to user and is not already submitted (Double Submit Prevention)
    result_record = execute_query(
        "SELECT * FROM results WHERE id = %s AND student_id = %s AND exam_id = %s",
        (result_id, user_id, exam_id),
        fetchone=True
    )

    if not result_record:
        return jsonify({"status": "error", "message": "Invalid exam session."}), 404

    if result_record["is_submitted"] == 1:
        return jsonify({"status": "error", "message": "Exam has already been submitted."}), 409

    # 2. Evaluate submission
    questions = execute_query("SELECT id, correct_option, marks FROM questions WHERE exam_id = %s", (exam_id,), fetchall=True) or []
    
    total_correct = 0
    total_wrong = 0
    total_unanswered = 0
    score_obtained = 0.0
    total_possible_score = 0.0

    # Clean old student answer entries if any
    execute_query("DELETE FROM student_answers WHERE result_id = %s", (result_id,), commit=True)

    for q in questions:
        q_id = str(q["id"])
        q_marks = float(q["marks"])
        total_possible_score += q_marks

        selected_opt = user_answers.get(q_id)
        is_correct = 0
        marks_got = 0.0

        if not selected_opt or selected_opt not in ['A', 'B', 'C', 'D']:
            total_unanswered += 1
            selected_opt = None
        elif selected_opt == q["correct_option"]:
            total_correct += 1
            is_correct = 1
            marks_got = q_marks
            score_obtained += q_marks
        else:
            total_wrong += 1

        # Record answer details
        execute_query(
            "INSERT INTO student_answers (result_id, question_id, selected_option, is_correct, marks_obtained) VALUES (%s, %s, %s, %s, %s)",
            (result_id, q["id"], selected_opt, is_correct, marks_got),
            commit=True
        )

    # 3. Calculate percentage and Pass/Fail status (Pass mark = 40%)
    percentage = (score_obtained / total_possible_score * 100.0) if total_possible_score > 0 else 0.0
    pass_mark = float(result_record.get("pass_percentage") or 40.0)
    status = "PASS" if percentage >= pass_mark else "FAIL"

    # 4. Finalize result record
    update_query = """
        UPDATE results
        SET submit_time = NOW(),
            score = %s,
            total_possible_score = %s,
            percentage = %s,
            status = %s,
            total_correct = %s,
            total_wrong = %s,
            total_unanswered = %s,
            is_submitted = 1
        WHERE id = %s
    """
    execute_query(
        update_query,
        (score_obtained, total_possible_score, percentage, status, total_correct, total_wrong, total_unanswered, result_id),
        commit=True
    )

    return jsonify({
        "status": "success",
        "message": "Exam submitted and evaluated successfully!",
        "result": {
            "result_id": result_id,
            "score": score_obtained,
            "total_possible_score": total_possible_score,
            "percentage": round(percentage, 2),
            "status": status,
            "total_correct": total_correct,
            "total_wrong": total_wrong,
            "total_unanswered": total_unanswered
        }
    }), 200


@student_bp.route("/results/<int:result_id>", methods=["GET"])
@student_required
def get_result_details(result_id):
    """Returns detailed result card with answer breakdown for student."""
    user_id = session["user"]["id"]

    query = """
        SELECT r.id, r.score, r.total_possible_score, r.percentage, r.status, r.start_time, r.submit_time,
               r.total_correct, r.total_wrong, r.total_unanswered,
               e.title as exam_title, e.duration_minutes, e.pass_percentage,
               c.course_name, c.course_code
        FROM results r
        JOIN exams e ON r.exam_id = e.id
        JOIN courses c ON e.course_id = c.id
        WHERE r.id = %s AND r.student_id = %s AND r.is_submitted = 1
    """
    result = execute_query(query, (result_id, user_id), fetchone=True)
    if not result:
        return jsonify({"status": "error", "message": "Result record not found."}), 404

    # Detailed answer key breakdown
    answers_query = """
        SELECT sa.question_id, sa.selected_option, sa.is_correct, sa.marks_obtained,
               q.question_text, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option, q.marks
        FROM student_answers sa
        JOIN questions q ON sa.question_id = q.id
        WHERE sa.result_id = %s
        ORDER BY q.id ASC
    """
    answers = execute_query(answers_query, (result_id,), fetchall=True) or []

    return jsonify({"status": "success", "result": result, "answers": answers}), 200
