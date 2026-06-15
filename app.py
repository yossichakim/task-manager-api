import os

import sqlite3

from flask import Flask, jsonify, request

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required
)

from werkzeug.security import check_password_hash, generate_password_hash

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT_SECRET_KEY is not configured")

jwt = JWTManager(app)

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

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username:
        return jsonify({
            "error": "Username is required"
        }), 400

    if not password:
        return jsonify({
            "error": "Password is required"
        }), 400

    if len(username) < 3:
        return jsonify({
            "error": "Username must contain at least 3 characters"
        }), 400

    if len(password) < 6:
        return jsonify({
            "error": "Password must contain at least 6 characters"
        }), 400

    password_hash = generate_password_hash(password)

    connection = get_database_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, password_hash)
        )

        connection.commit()

        user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        connection.close()

        return jsonify({
            "error": "Username already exists"
        }), 409

    connection.close()

    return jsonify({
        "id": user_id,
        "username": username,
        "message": "User registered successfully"
    }), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username:
        return jsonify({
            "error": "Username is required"
        }), 400

    if not password:
        return jsonify({
            "error": "Password is required"
        }), 400

    connection = get_database_connection()

    user = connection.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    connection.close()

    if user is None:
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    access_token = create_access_token(identity=str(user["id"]))

    return jsonify({
    "access_token": access_token,
    "user": {
        "id": user["id"],
        "username": user["username"]
    },
    "message": "Login successful"
    })


@app.route("/tasks", methods=["GET"])
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


@app.route("/tasks/<int:task_id>", methods=["GET"])
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


@app.route("/tasks", methods=["POST"])
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
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    return jsonify(dict(new_task)), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
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
    (task_id, current_user_id)).fetchone()

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
    ))

    connection.commit()

    updated_task = connection.execute(
    """
    SELECT * FROM tasks
    WHERE id = ? AND user_id = ?
    """,
    (task_id, current_user_id)).fetchone()

    connection.close()

    return jsonify(dict(updated_task))


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
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


if __name__ == "__main__":
    app.run(debug=True)