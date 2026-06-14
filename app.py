import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__)

DATABASE_NAME = "tasks.db"
ALLOWED_STATUSES = {"pending", "completed"}

def get_database_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Task Manager API is running"
    })


@app.route("/about", methods=["GET"])
def about():
    return jsonify({
        "project": "Task Manager API",
        "language": "Python",
        "framework": "Flask"
    })

@app.route("/tasks", methods=["GET"])
def get_tasks():
    status = request.args.get("status")
    category = request.args.get("category")

    query = "SELECT * FROM tasks"
    parameters = []
    conditions = []

    if status:
        conditions.append("status = ?")
        parameters.append(status)

    if category:
        conditions.append("category = ?")
        parameters.append(category)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    connection = get_database_connection()

    tasks = connection.execute(
        query,
        parameters
    ).fetchall()

    connection.close()

    return jsonify([
        dict(task) for task in tasks
    ])


@app.route("/tasks", methods=["POST"])
def create_task():
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
        INSERT INTO tasks (title, description, category, status)
        VALUES (?, ?, ?, ?)
        """,
        (title, description, category, status)
    )

    connection.commit()

    task_id = cursor.lastrowid

    new_task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return jsonify(dict(new_task)), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    connection = get_database_connection()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    if task is None:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify(dict(task))

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    connection = get_database_connection()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
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
        WHERE id = ?
        """,
        (title.strip(), description, category, status, task_id)
    )

    connection.commit()

    updated_task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return jsonify(dict(updated_task))


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    connection = get_database_connection()

    task = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if task is None:
        connection.close()

        return jsonify({
            "error": "Task not found"
        }), 404

    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Task deleted successfully"
    })


if __name__ == "__main__":
    app.run(debug=True)