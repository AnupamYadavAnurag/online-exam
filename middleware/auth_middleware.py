from functools import wraps
from flask import session, jsonify, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
            return jsonify({"status": "error", "message": "Authentication required."}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"status": "error", "message": "Authentication required."}), 401
        if session["user"].get("role") != "admin":
            return jsonify({"status": "error", "message": "Access denied. Admin role required."}), 403
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return jsonify({"status": "error", "message": "Authentication required."}), 401
        if session["user"].get("role") != "student":
            return jsonify({"status": "error", "message": "Access denied. Student role required."}), 403
        return f(*args, **kwargs)
    return decorated_function
