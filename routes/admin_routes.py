from flask import Blueprint, request, jsonify, session
from middleware.auth_middleware import admin_required
from db.connection import execute_query
from utils.validators import validate_exam, validate_question

admin_bp = Blueprint("admin", __name__)

# --- 1. Dashboard Overview Stats ---
@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_stats():
    """Returns aggregated counts for admin dashboard."""
    try:
        students_count = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'student'", fetchone=True)["count"]
        blocked_count = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND status = 'blocked'", fetchone=True)["count"]
        courses_count = execute_query("SELECT COUNT(*) as count FROM courses", fetchone=True)["count"]
        exams_count = execute_query("SELECT COUNT(*) as count FROM exams", fetchone=True)["count"]
        published_exams = execute_query("SELECT COUNT(*) as count FROM exams WHERE is_published = 1", fetchone=True)["count"]

        return jsonify({
            "status": "success",
            "stats": {
                "students": students_count,
                "blocked_students": blocked_count,
                "courses": courses_count,
                "exams": exams_count,
                "published_exams": published_exams
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# --- 2. Departments Helper ---
@admin_bp.route("/departments", methods=["GET"])
@admin_required
def get_departments():
    """Returns departments for course/exam dropdowns."""
    depts = execute_query("SELECT * FROM departments ORDER BY dept_code", fetchall=True)
    return jsonify({"status": "success", "departments": depts or []}), 200


# --- 3. Student Management APIs ---
@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_students():
    """Lists all registered student accounts."""
    query = """
        SELECT u.id, u.full_name, u.student_id, u.email, u.phone, u.username, u.status, u.dob, u.created_at,
               c.course_name, c.course_code, d.dept_name
        FROM users u
        LEFT JOIN courses c ON u.course_id = c.id
        LEFT JOIN departments d ON u.dept_id = d.id
        WHERE u.role = 'student'
        ORDER BY u.id DESC
    """
    students = execute_query(query, fetchall=True)
    return jsonify({"status": "success", "students": students or []}), 200

@admin_bp.route("/students/<int:student_id>/status", methods=["PUT"])
@admin_required
def update_student_status(student_id):
    """Blocks or unblocks a student account."""
    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in ["active", "blocked"]:
        return jsonify({"status": "error", "message": "Status must be 'active' or 'blocked'."}), 400

    user = execute_query("SELECT id, role FROM users WHERE id = %s", (student_id,), fetchone=True)
    if not user or user["role"] != "student":
        return jsonify({"status": "error", "message": "Student account not found."}), 404

    execute_query("UPDATE users SET status = %s WHERE id = %s", (new_status, student_id), commit=True)
    action_text = "blocked" if new_status == "blocked" else "unblocked"
    return jsonify({"status": "success", "message": f"Student account has been {action_text}."}), 200

@admin_bp.route("/students/<int:student_id>", methods=["DELETE"])
@admin_required
def delete_student(student_id):
    """Deletes a student account."""
    user = execute_query("SELECT id, role FROM users WHERE id = %s", (student_id,), fetchone=True)
    if not user or user["role"] != "student":
        return jsonify({"status": "error", "message": "Student account not found."}), 404

    execute_query("DELETE FROM users WHERE id = %s", (student_id,), commit=True)
    return jsonify({"status": "success", "message": "Student account deleted successfully."}), 200


# --- 4. Course Management APIs ---
@admin_bp.route("/courses", methods=["GET"])
@admin_required
def get_courses():
    """Lists all academic courses."""
    query = """
        SELECT c.id, c.course_code, c.course_name, c.description, c.dept_id, d.dept_name,
               (SELECT COUNT(*) FROM exams e WHERE e.course_id = c.id) as total_exams
        FROM courses c
        JOIN departments d ON c.dept_id = d.id
        ORDER BY c.course_code
    """
    courses = execute_query(query, fetchall=True)
    return jsonify({"status": "success", "courses": courses or []}), 200

@admin_bp.route("/courses", methods=["POST"])
@admin_required
def create_course():
    """Creates a new course."""
    data = request.get_json() or {}
    code = data.get("course_code", "").strip()
    name = data.get("course_name", "").strip()
    dept_id = data.get("dept_id")
    desc = data.get("description", "").strip()

    if not code or not name or not dept_id:
        return jsonify({"status": "error", "message": "Course Code, Name, and Department are required."}), 400

    # Check unique course code
    existing = execute_query("SELECT id FROM courses WHERE course_code = %s", (code,), fetchone=True)
    if existing:
        return jsonify({"status": "error", "message": "Course code already exists."}), 409

    query = "INSERT INTO courses (course_code, course_name, dept_id, description) VALUES (%s, %s, %s, %s)"
    course_id = execute_query(query, (code, name, dept_id, desc), commit=True)
    return jsonify({"status": "success", "message": "Course created successfully!", "course_id": course_id}), 201

@admin_bp.route("/courses/<int:course_id>", methods=["PUT"])
@admin_required
def update_course(course_id):
    """Updates course details."""
    data = request.get_json() or {}
    code = data.get("course_code", "").strip()
    name = data.get("course_name", "").strip()
    dept_id = data.get("dept_id")
    desc = data.get("description", "").strip()

    if not code or not name or not dept_id:
        return jsonify({"status": "error", "message": "Course Code, Name, and Department are required."}), 400

    query = "UPDATE courses SET course_code = %s, course_name = %s, dept_id = %s, description = %s WHERE id = %s"
    execute_query(query, (code, name, dept_id, desc, course_id), commit=True)
    return jsonify({"status": "success", "message": "Course updated successfully."}), 200

@admin_bp.route("/courses/<int:course_id>", methods=["DELETE"])
@admin_required
def delete_course(course_id):
    """Deletes a course."""
    execute_query("DELETE FROM courses WHERE id = %s", (course_id,), commit=True)
    return jsonify({"status": "success", "message": "Course deleted successfully."}), 200


# --- 5. Exam Management APIs ---
@admin_bp.route("/exams", methods=["GET"])
@admin_required
def get_exams():
    """Lists all exams."""
    query = """
        SELECT e.id, e.title, e.description, e.duration_minutes, e.total_marks, e.pass_percentage, e.is_published, e.created_at,
               c.course_name, c.course_code,
               (SELECT COUNT(*) FROM questions q WHERE q.exam_id = e.id) as question_count
        FROM exams e
        JOIN courses c ON e.course_id = c.id
        ORDER BY e.id DESC
    """
    exams = execute_query(query, fetchall=True)
    return jsonify({"status": "success", "exams": exams or []}), 200

@admin_bp.route("/exams", methods=["POST"])
@admin_required
def create_exam():
    """Creates a new exam with duration boundary checks (min 5, max 180)."""
    data = request.get_json() or {}
    is_valid, errors = validate_exam(data)

    if not is_valid:
        return jsonify({"status": "error", "message": "Exam validation failed", "errors": errors}), 400

    admin_id = session["user"]["id"]
    query = """
        INSERT INTO exams (course_id, title, description, duration_minutes, total_marks, pass_percentage, is_published, created_by)
        VALUES (%s, %s, %s, %s, %s, 40.00, 0, %s)
    """
    params = (
        data["course_id"],
        data["title"].strip(),
        data.get("description", "").strip(),
        int(data["duration_minutes"]),
        int(data.get("total_marks", 10)),
        admin_id
    )

    exam_id = execute_query(query, params, commit=True)
    return jsonify({"status": "success", "message": "Exam created successfully!", "exam_id": exam_id}), 201

@admin_bp.route("/exams/<int:exam_id>", methods=["PUT"])
@admin_required
def update_exam(exam_id):
    """Updates existing exam."""
    data = request.get_json() or {}
    is_valid, errors = validate_exam(data)

    if not is_valid:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    query = """
        UPDATE exams
        SET course_id = %s, title = %s, description = %s, duration_minutes = %s, total_marks = %s
        WHERE id = %s
    """
    params = (
        data["course_id"],
        data["title"].strip(),
        data.get("description", "").strip(),
        int(data["duration_minutes"]),
        int(data.get("total_marks", 10)),
        exam_id
    )
    execute_query(query, params, commit=True)
    return jsonify({"status": "success", "message": "Exam updated successfully."}), 200

@admin_bp.route("/exams/<int:exam_id>", methods=["DELETE"])
@admin_required
def delete_exam(exam_id):
    """Deletes an exam and associated questions/results."""
    execute_query("DELETE FROM exams WHERE id = %s", (exam_id,), commit=True)
    return jsonify({"status": "success", "message": "Exam deleted successfully."}), 200

@admin_bp.route("/exams/<int:exam_id>/publish", methods=["PUT"])
@admin_required
def toggle_publish_exam(exam_id):
    """Publishes or unpublishes an exam."""
    data = request.get_json() or {}
    is_published = 1 if data.get("is_published") in [1, True, "1"] else 0

    execute_query("UPDATE exams SET is_published = %s WHERE id = %s", (is_published, exam_id), commit=True)
    action_text = "published" if is_published == 1 else "unpublished"
    return jsonify({"status": "success", "message": f"Exam has been {action_text} successfully."}), 200


# --- 6. Question Management APIs ---
@admin_bp.route("/exams/<int:exam_id>/questions", methods=["GET"])
@admin_required
def get_exam_questions(exam_id):
    """Returns questions for a specified exam."""
    query = "SELECT * FROM questions WHERE exam_id = %s ORDER BY id ASC"
    questions = execute_query(query, (exam_id,), fetchall=True)
    return jsonify({"status": "success", "questions": questions or []}), 200

@admin_bp.route("/exams/<int:exam_id>/questions", methods=["POST"])
@admin_required
def add_question(exam_id):
    """Adds a new MCQ question to an exam."""
    data = request.get_json() or {}
    is_valid, errors = validate_question(data)

    if not is_valid:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    query = """
        INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_option, marks, difficulty_level, topic)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        exam_id,
        data["question_text"].strip(),
        data["option_a"].strip(),
        data["option_b"].strip(),
        data["option_c"].strip(),
        data["option_d"].strip(),
        data["correct_option"].strip().upper(),
        int(data.get("marks", 1)),
        data.get("difficulty_level", "MEDIUM"),
        data.get("topic", "").strip()
    )

    q_id = execute_query(query, params, commit=True)
    return jsonify({"status": "success", "message": "Question added successfully!", "question_id": q_id}), 201

@admin_bp.route("/questions/<int:question_id>", methods=["PUT"])
@admin_required
def update_question(question_id):
    """Updates an existing question."""
    data = request.get_json() or {}
    is_valid, errors = validate_question(data)

    if not is_valid:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    query = """
        UPDATE questions
        SET question_text = %s, option_a = %s, option_b = %s, option_c = %s, option_d = %s,
            correct_option = %s, marks = %s, difficulty_level = %s, topic = %s
        WHERE id = %s
    """
    params = (
        data["question_text"].strip(),
        data["option_a"].strip(),
        data["option_b"].strip(),
        data["option_c"].strip(),
        data["option_d"].strip(),
        data["correct_option"].strip().upper(),
        int(data.get("marks", 1)),
        data.get("difficulty_level", "MEDIUM"),
        data.get("topic", "").strip(),
        question_id
    )

    execute_query(query, params, commit=True)
    return jsonify({"status": "success", "message": "Question updated successfully."}), 200

@admin_bp.route("/questions/<int:question_id>", methods=["DELETE"])
@admin_required
def delete_question(question_id):
    """Deletes a question."""
    execute_query("DELETE FROM questions WHERE id = %s", (question_id,), commit=True)
    return jsonify({"status": "success", "message": "Question deleted successfully."}), 200


# --- 7. Student Exam Results Management APIs ---
@admin_bp.route("/results", methods=["GET"])
@admin_required
def get_all_results():
    """Returns list of student exam submission results for Admin review."""
    query = """
        SELECT r.id, r.score, r.total_possible_score, r.percentage, r.status, r.start_time, r.submit_time,
               r.total_correct, r.total_wrong, r.total_unanswered,
               u.full_name as student_name, u.student_id, u.email as student_email,
               e.title as exam_title, c.course_code
        FROM results r
        JOIN users u ON r.student_id = u.id
        JOIN exams e ON r.exam_id = e.id
        JOIN courses c ON e.course_id = c.id
        WHERE r.is_submitted = 1
        ORDER BY r.id DESC
    """
    results = execute_query(query, fetchall=True)
    return jsonify({"status": "success", "results": results or []}), 200

@admin_bp.route("/results/<int:result_id>", methods=["DELETE"])
@admin_required
def delete_result(result_id):
    """Deletes a result entry (resets attempt for student)."""
    execute_query("DELETE FROM results WHERE id = %s", (result_id,), commit=True)
    return jsonify({"status": "success", "message": "Result entry deleted. Student attempt has been reset."}), 200

