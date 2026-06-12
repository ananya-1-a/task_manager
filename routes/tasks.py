from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Task

tasks_bp = Blueprint("tasks", __name__)

VALID_STATUSES = ["pending", "in_progress", "done"]
VALID_PRIORITIES = ["low", "medium", "high"]


# ─── Get all tasks for current user ──────────────────────────────────────────
@tasks_bp.route("", methods=["GET"])
@jwt_required()
def get_tasks():
    """
    Get all tasks for the logged-in user
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, in_progress, done]
      - in: query
        name: priority
        type: string
        enum: [low, medium, high]
    responses:
      200:
        description: List of tasks
    """
    user_id = get_jwt_identity()
    query = Task.query.filter_by(user_id=user_id)

    status = request.args.get("status")
    priority = request.args.get("priority")

    if status:
        if status not in VALID_STATUSES:
            return jsonify({"error": f"Status must be one of {VALID_STATUSES}"}), 400
        query = query.filter_by(status=status)

    if priority:
        if priority not in VALID_PRIORITIES:
            return jsonify({"error": f"Priority must be one of {VALID_PRIORITIES}"}), 400
        query = query.filter_by(priority=priority)

    tasks = query.order_by(Task.created_at.desc()).all()
    return jsonify({
        "tasks": [t.to_dict() for t in tasks],
        "count": len(tasks)
    }), 200


# ─── Create task ──────────────────────────────────────────────────────────────
@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    """
    Create a new task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              example: Build REST API
            description:
              type: string
              example: Implement authentication and CRUD
            status:
              type: string
              enum: [pending, in_progress, done]
              example: pending
            priority:
              type: string
              enum: [low, medium, high]
              example: medium
    responses:
      201:
        description: Task created
      400:
        description: Validation error
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if len(title) > 200:
        return jsonify({"error": "Title must be under 200 characters"}), 400

    status = data.get("status", "pending")
    priority = data.get("priority", "medium")

    if status not in VALID_STATUSES:
        return jsonify({"error": f"Status must be one of {VALID_STATUSES}"}), 400
    if priority not in VALID_PRIORITIES:
        return jsonify({"error": f"Priority must be one of {VALID_PRIORITIES}"}), 400

    task = Task(
        title=title,
        description=data.get("description", "").strip(),
        status=status,
        priority=priority,
        user_id=user_id
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task created successfully",
        "task": task.to_dict()
    }), 201


# ─── Get single task ──────────────────────────────────────────────────────────
@tasks_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    """
    Get a single task by ID
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task details
      404:
        description: Task not found
    """
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({"task": task.to_dict()}), 200


# ─── Update task ──────────────────────────────────────────────────────────────
@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    """
    Update a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            status:
              type: string
              enum: [pending, in_progress, done]
            priority:
              type: string
              enum: [low, medium, high]
    responses:
      200:
        description: Task updated
      404:
        description: Task not found
    """
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return jsonify({"error": "Title cannot be empty"}), 400
        task.title = title

    if "description" in data:
        task.description = data["description"].strip()

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"Status must be one of {VALID_STATUSES}"}), 400
        task.status = data["status"]

    if "priority" in data:
        if data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": f"Priority must be one of {VALID_PRIORITIES}"}), 400
        task.priority = data["priority"]

    db.session.commit()

    return jsonify({
        "message": "Task updated successfully",
        "task": task.to_dict()
    }), 200


# ─── Delete task ──────────────────────────────────────────────────────────────
@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    """
    Delete a task
    ---
    tags:
      - Tasks
    security:
      - Bearer: []
    parameters:
      - in: path
        name: task_id
        type: integer
        required: true
    responses:
      200:
        description: Task deleted
      404:
        description: Task not found
    """
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted successfully"}), 200
