import os

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager

from app.auth_routes import auth_bp
from app.database import init_db
from app.jwt_handlers import register_jwt_handlers
from app.main_routes import main_bp
from app.task_routes import tasks_bp


load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["DATABASE"] = "tasks.db"

    if test_config is not None:
        app.config.update(test_config)

    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    jwt = JWTManager(app)

    register_jwt_handlers(jwt)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)

    with app.app_context():
        init_db()

    return app