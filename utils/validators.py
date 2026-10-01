import re
from datetime import datetime, date

def validate_registration(data):
    """
    Validates student registration data.
    Returns: (is_valid, errors_dict)
    """
    errors = {}

    # 1. Full Name check
    full_name = data.get("full_name", "").strip() if data.get("full_name") else ""
    if not full_name:
        errors["full_name"] = "Full Name is required."
    elif len(full_name) < 2:
        errors["full_name"] = "Full Name must be at least 2 characters."

    # 2. Student ID check
    student_id = data.get("student_id", "").strip() if data.get("student_id") else ""
    if not student_id:
        errors["student_id"] = "Student ID is required."
    elif not re.match(r"^[a-zA-Z0-9_-]+$", student_id):
        errors["student_id"] = "Student ID can only contain letters, numbers, hyphens, and underscores."

    # 3. Email check
    email = data.get("email", "").strip() if data.get("email") else ""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not email:
        errors["email"] = "Email is required."
    elif not re.match(email_regex, email):
        errors["email"] = "Invalid email address format."

    # 4. Phone check (10 digits)
    phone = data.get("phone", "").strip() if data.get("phone") else ""
    if not phone:
        errors["phone"] = "Phone number is required."
    elif not re.match(r"^\d{10}$", phone):
        errors["phone"] = "Phone number must be exactly 10 digits."

    # 5. Username check
    username = data.get("username", "").strip() if data.get("username") else ""
    if not username:
        errors["username"] = "Username is required."
    elif len(username) < 3 or len(username) > 30:
        errors["username"] = "Username must be between 3 and 30 characters."
    elif not re.match(r"^[a-zA-Z0-9_]+$", username):
        errors["username"] = "Username can only contain letters, numbers, and underscores."

    # 6. Password check (8 - 20 chars)
    password = data.get("password", "") if data.get("password") else ""
    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8 or len(password) > 20:
        errors["password"] = "Password must be between 8 and 20 characters."

    # 7. Confirm Password check
    confirm_password = data.get("confirm_password", "") if data.get("confirm_password") else ""
    if not confirm_password:
        errors["confirm_password"] = "Confirm Password is required."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    # 8. Course check
    course_id = data.get("course_id")
    if not course_id:
        errors["course_id"] = "Course selection is required."

    # 9. Date of Birth check (Not future, age >= 15)
    dob_str = data.get("dob", "").strip() if data.get("dob") else ""
    if not dob_str:
        errors["dob"] = "Date of birth is required."
    else:
        try:
            dob_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
            today = date.today()
            if dob_date > today:
                errors["dob"] = "Date of birth cannot be a future date."
            else:
                age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
                if age < 15:
                    errors["dob"] = "Minimum age required is 15 years."
        except ValueError:
            errors["dob"] = "Invalid date format. Use YYYY-MM-DD."

    is_valid = len(errors) == 0
    return is_valid, errors

def validate_password_reset(password, confirm_password):
    """
    Validates new password and confirm_password for password reset flow.
    Returns: (is_valid, errors_dict)
    """
    errors = {}

    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8 or len(password) > 20:
        errors["password"] = "Password must be between 8 and 20 characters."

    if not confirm_password:
        errors["confirm_password"] = "Confirm password is required."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords do not match."

    is_valid = len(errors) == 0
    return is_valid, errors

def validate_exam(data):
    """
    Validates exam creation & modification fields.
    Duration boundary rules: Min 5 minutes, Max 180 minutes.
    Returns: (is_valid, errors_dict)
    """
    errors = {}

    title = data.get("title", "").strip() if data.get("title") else ""
    if not title:
        errors["title"] = "Exam title is required."
    elif len(title) < 3:
        errors["title"] = "Exam title must be at least 3 characters."

    course_id = data.get("course_id")
    if not course_id:
        errors["course_id"] = "Course selection is required."

    # Duration boundary check (5 - 180 mins)
    duration = data.get("duration_minutes")
    if duration is None or duration == "":
        errors["duration_minutes"] = "Exam duration is required."
    else:
        try:
            duration_val = int(duration)
            if duration_val < 5 or duration_val > 180:
                errors["duration_minutes"] = "Exam duration must be between 5 and 180 minutes."
        except (ValueError, TypeError):
            errors["duration_minutes"] = "Duration must be a valid integer number."

    is_valid = len(errors) == 0
    return is_valid, errors

def validate_question(data):
    """
    Validates MCQ question creation data.
    Returns: (is_valid, errors_dict)
    """
    errors = {}

    question_text = data.get("question_text", "").strip() if data.get("question_text") else ""
    if not question_text:
        errors["question_text"] = "Question text is required."

    option_a = data.get("option_a", "").strip() if data.get("option_a") else ""
    option_b = data.get("option_b", "").strip() if data.get("option_b") else ""
    option_c = data.get("option_c", "").strip() if data.get("option_c") else ""
    option_d = data.get("option_d", "").strip() if data.get("option_d") else ""

    if not option_a: errors["option_a"] = "Option A is required."
    if not option_b: errors["option_b"] = "Option B is required."
    if not option_c: errors["option_c"] = "Option C is required."
    if not option_d: errors["option_d"] = "Option D is required."

    correct_option = data.get("correct_option", "").strip().upper() if data.get("correct_option") else ""
    if not correct_option or correct_option not in ['A', 'B', 'C', 'D']:
        errors["correct_option"] = "Correct option must be A, B, C, or D."

    is_valid = len(errors) == 0
    return is_valid, errors
