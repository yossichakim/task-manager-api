from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.database import get_database_connection


tasks_bp = Blueprint("tasks", __name__)

ALLOWED_STATUSES = {"pending", "completed"}


@tasks_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    current_user_id = int(get_jwt_identity())

    status = request.args.get("status")
    category = request.args.get("category")

    query = "SELECT * FROM tasks WHERE user_id = ?"
    parameters = [current_user_id]
    conditions = []

    if status:
        conditions.append("status = ?")
        parameters.append(status)

    if category:
        conditions.append("category = ?")
        parameters.append(category)

    if conditions:
        query += " AND " + " AND ".join(conditions)

    connection = get_database_connection()

    tasks = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return jsonify([
        dict(task) for task in tasks
    ])


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    current_user_id = int(get_jwt_identity())

    connection = get_database_connection()

    task = connection.execute(
        """
        SELECT * FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, current_user_id)
    ).fetchone()

    connection.close()

    if task is None:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(dict(task))


@tasks_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    current_user_id = int(get_jwt_identity())

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    title = data.get("title", "").strip()

    if not title:
        return jsonify({
            "error": "Title is required"
        }), 400

    description = data.get("description", "")
    category = data.get("category", "general")
    status = "pending"

    connection = get_database_connection()

    cursor = connection.execute(
        """
        INSERT INTO tasks (
            title,
            description,
            category,
            status,
            user_id
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            description,
            category,
            status,
            current_user_id
        )
    )

    connection.commit()
    task_id = cursor.lastrowid

    new_task = connection.execute(
        """
        SELECT * FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, current_user_id)
    ).fetchone()

    connection.close()

    return jsonify(dict(new_task)), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    current_user_id = int(get_jwt_identity())

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    connection = get_database_connection()

    task = connection.execute(
        """
        SELECT * FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, current_user_id)
    ).fetchone()

    if task is None:
        connection.close()

        return jsonify({
            "error": "Task not found"
        }), 404

    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    category = data.get("category", task["category"])
    status = data.get("status", task["status"])

    if status not in ALLOWED_STATUSES:
        connection.close()

        return jsonify({
            "error": "Status must be either 'pending' or 'completed'"
        }), 400

    if not title.strip():
        connection.close()

        return jsonify({
            "error": "Title cannot be empty"
        }), 400

    connection.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, category = ?, status = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            title.strip(),
            description,
            category,
            status,
            task_id,
            current_user_id
        )
    )

    connection.commit()

    updated_task = connection.execute(
        """
        SELECT * FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, current_user_id)
    ).fetchone()

    connection.close()

    return jsonify(dict(updated_task))


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    current_user_id = int(get_jwt_identity())

    connection = get_database_connection()

    task = connection.execute(
        """
        SELECT * FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, current_user_id)
    ).fetchone()

    if task is None:
        connection.close()

        return jsonify({
            "error": "Task not found"
        }), 404

    connection.execute(
        """
        DELETE FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, current_user_id)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Task deleted successfully"
    })