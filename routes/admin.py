from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middleware.auth_middleware import admin_required
from extensions import db
from models import User, Task

admin_bp = Blueprint("admin", __name__)


# ─── Get all users ────────────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    """
    Get all users (admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users
      403:
        description: Admin access required
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({
        "users": [u.to_dict() for u in users],
        "count": len(users)
    }), 200


# ─── Get all tasks (any user) ─────────────────────────────────────────────────
@admin_bp.route("/tasks", methods=["GET"])
@admin_required
def get_all_tasks():
    """
    Get all tasks across all users (admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: All tasks
      403:
        description: Admin access required
    """
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify({
        "tasks": [t.to_dict() for t in tasks],
        "count": len(tasks)
    }), 200
@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """
    Delete a user by ID (admin only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    responses:
      200:
        description: User deleted
      404:
        description: User not found
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user.username} deleted successfully"}), 200
