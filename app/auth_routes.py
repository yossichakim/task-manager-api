import sqlite3

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import get_database_connection


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
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


@auth_bp.route("/login", methods=["POST"])
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
        """
        SELECT * FROM users
        WHERE username = ?
        """,
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

    access_token = create_access_token(
        identity=str(user["id"])
    )

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user["id"],
            "username": user["username"]
        },
        "message": "Login successful"
    })