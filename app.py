from flask import Flask, render_template, redirect, url_for, session, send_from_directory
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.student_routes import student_bp
from routes.test_routes import test_bp
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config.from_object(Config)
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(admin_bp, url_prefix="/api/admin")
app.register_blueprint(student_bp, url_prefix="/api/student")
app.register_blueprint(test_bp, url_prefix="/api/test")

# Page Routes
@app.route("/")
def index():
    if "user" in session:
        user = session["user"]
        if user.get("role") == "admin":
            return redirect("/admin-dashboard")
        return redirect("/student-dashboard")
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")

@app.route("/reset-password")
def reset_password_page():
    return render_template("reset_password.html")

@app.route("/student-dashboard")
def student_dashboard():
    if "user" not in session or session["user"].get("role") != "student":
        return redirect("/login")
    return render_template("student_dashboard.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    if "user" not in session or session["user"].get("role") != "admin":
        return redirect("/login")
    return render_template("admin_dashboard.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
