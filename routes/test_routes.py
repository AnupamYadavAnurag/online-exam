import os
from flask import Blueprint, jsonify
from db.init_db import init_database

test_bp = Blueprint("test", __name__)

@test_bp.route("/reset", methods=["POST"])
def reset_database():
    """Development-only endpoint to reset the DB to fresh seed data before tests."""
    env = os.getenv("FLASK_ENV", "development")
    if env not in ["development", "testing"]:
        return jsonify({"status": "error", "message": "Reset endpoint disabled in production."}), 403

    success = init_database()
    if success:
        return jsonify({"status": "success", "message": "Database reset to initial seed state."}), 200
    else:
        return jsonify({"status": "error", "message": "Database reset failed."}), 500
