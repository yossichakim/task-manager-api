from flask import Blueprint, jsonify


main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Task Manager API is running"
    })


@main_bp.route("/about", methods=["GET"])
def about():
    return jsonify({
        "project": "Task Manager API",
        "language": "Python",
        "framework": "Flask"
    })