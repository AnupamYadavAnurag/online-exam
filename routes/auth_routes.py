import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from db.connection import execute_query
from utils.validators import validate_registration, validate_password_reset

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/courses", methods=["GET"])
def get_courses():
    """Returns available courses for registration dropdown."""
    try:
        courses = execute_query("SELECT id, course_code, course_name FROM courses ORDER BY course_code", fetchall=True)
        return jsonify({"status": "success", "courses": courses or []}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@auth_bp.route("/register", methods=["POST"])
def register():
    """Registers a new student account."""
    data = request.get_json() or {}
    
    # 1. Validate fields
    is_valid, errors = validate_registration(data)
    if not is_valid:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    # 2. Check for unique constraints in DB
    existing_username = execute_query("SELECT id FROM users WHERE username = %s", (data["username"].strip(),), fetchone=True)
    if existing_username:
        errors["username"] = "Username is already registered."

    existing_email = execute_query("SELECT id FROM users WHERE email = %s", (data["email"].strip(),), fetchone=True)
    if existing_email:
        errors["email"] = "Email address is already registered."

    existing_student_id = execute_query("SELECT id FROM users WHERE student_id = %s", (data["student_id"].strip(),), fetchone=True)
    if existing_student_id:
        errors["student_id"] = "Student ID is already registered."

    if errors:
        return jsonify({"status": "error", "message": "Duplicate registration details", "errors": errors}), 409

    # 3. Hash password and insert user
    hashed_password = generate_password_hash(data["password"])
    query = """
        INSERT INTO users (full_name, student_id, email, phone, username, password, status, role, course_id, dob)
        VALUES (%s, %s, %s, %s, %s, %s, 'active', 'student', %s, %s)
    """
    params = (
        data["full_name"].strip(),
        data["student_id"].strip(),
        data["email"].strip(),
        data["phone"].strip(),
        data["username"].strip(),
        hashed_password,
        data["course_id"],
        data["dob"].strip()
    )

    try:
        user_id = execute_query(query, params, commit=True)
        return jsonify({
            "status": "success",
            "message": "Registration successful! You can now log in.",
            "user_id": user_id
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": "Database error during registration."}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticates student or admin users."""
    data = request.get_json() or {}
    login_id = data.get("username", "").strip()
    password = data.get("password", "")
    remember_me = data.get("remember_me", False)

    # Empty validation
    errors = {}
    if not login_id:
        errors["username"] = "Username or Email is required."
    if not password:
        errors["password"] = "Password is required."

    if errors:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    # Query user safely via parameterized query
    query = "SELECT * FROM users WHERE username = %s OR email = %s"
    user = execute_query(query, (login_id, login_id), fetchone=True)

    # Generic error if user not found or password invalid (Prevents Account Enumeration)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401

    # Check if account is blocked
    if user["status"] == "blocked":
        return jsonify({"status": "error", "message": "Your account is blocked. Please contact administrator."}), 403

    # Set up session
    session.clear()
    session["user"] = {
        "id": user["id"],
        "full_name": user["full_name"],
        "student_id": user.get("student_id"),
        "email": user["email"],
        "username": user["username"],
        "role": user["role"],
        "status": user["status"]
    }

    if remember_me:
        session.permanent = True

    return jsonify({
        "status": "success",
        "message": f"Welcome back, {user['full_name']}!",
        "user": session["user"]
    }), 200

@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logs out current user and destroys session."""
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully."}), 200

@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Returns details of currently authenticated user."""
    user = session.get("user")
    if not user:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    return jsonify({"status": "success", "user": user}), 200

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Generates password reset token (Demo mode: returns link directly)."""
    data = request.get_json() or {}
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"status": "error", "message": "Validation failed", "errors": {"email": "Email is required."}}), 400

    user = execute_query("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)
    if not user:
        # Generic response to prevent user enumeration
        return jsonify({
            "status": "success",
            "message": "If that email is registered, a password reset link has been generated."
        }), 200

    # Generate token expiring in 15 minutes
    reset_token = secrets.token_hex(20)
    expires_at = datetime.now() + timedelta(minutes=15)

    # Invalidate previous unused tokens for this user
    execute_query("UPDATE password_resets SET is_used = 1 WHERE user_id = %s", (user["id"],), commit=True)

    # Insert new token
    insert_query = "INSERT INTO password_resets (user_id, email, reset_token, expires_at) VALUES (%s, %s, %s, %s)"
    execute_query(insert_query, (user["id"], email, reset_token, expires_at.strftime("%Y-%m-%d %H:%M:%S")), commit=True)

    reset_url = f"/reset-password?token={reset_token}"
    print(f"\n🔑 DEMO PASSWORD RESET LINK: http://localhost:5000{reset_url}\n")

    return jsonify({
        "status": "success",
        "message": "Password reset token generated successfully (Demo Mode).",
        "demo_reset_token": reset_token,
        "demo_reset_url": reset_url
    }), 200

@auth_bp.route("/verify-token/<token>", methods=["GET"])
def verify_token(token):
    """Verifies validity of password reset token."""
    query = "SELECT * FROM password_resets WHERE reset_token = %s AND is_used = 0 AND expires_at > NOW()"
    record = execute_query(query, (token,), fetchone=True)

    if not record:
        return jsonify({"status": "error", "message": "Invalid or expired reset token."}), 400

    return jsonify({"status": "success", "message": "Valid reset token.", "email": record["email"]}), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Resets user password using a valid reset token."""
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    new_password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not token:
        return jsonify({"status": "error", "message": "Reset token is missing."}), 400

    # Validate new password
    is_valid, errors = validate_password_reset(new_password, confirm_password)
    if not is_valid:
        return jsonify({"status": "error", "message": "Validation failed", "errors": errors}), 400

    # Verify token
    query = "SELECT * FROM password_resets WHERE reset_token = %s AND is_used = 0 AND expires_at > NOW()"
    reset_record = execute_query(query, (token,), fetchone=True)

    if not reset_record:
        return jsonify({"status": "error", "message": "Invalid or expired reset token."}), 400

    # Update password and mark token used
    hashed_password = generate_password_hash(new_password)
    execute_query("UPDATE users SET password = %s WHERE id = %s", (hashed_password, reset_record["user_id"]), commit=True)
    execute_query("UPDATE password_resets SET is_used = 1 WHERE id = %s", (reset_record["id"],), commit=True)

    return jsonify({
        "status": "success",
        "message": "Password reset successful! You can now log in with your new password."
    }), 200
