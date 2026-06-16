import os

from dotenv import load_dotenv
from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from app.auth_routes import auth_bp
from app.database import init_db
from app.jwt_handlers import register_jwt_handlers
from app.main_routes import main_bp
from app.task_routes import tasks_bp


load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)

    swagger_url = "/docs"
    api_url = "/openapi.yaml"

    swagger_ui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            "app_name": "Task Manager API"
        }
    )

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

    app.register_blueprint(
        swagger_ui_blueprint,
        url_prefix=swagger_url
    ) 

    @app.route("/openapi.yaml")
    def openapi_spec():
        project_root = os.path.dirname(app.root_path)
        return send_from_directory(project_root, "openapi.yaml")
    
    with app.app_context():
        init_db()

    return app