from flask import Flask
import os
from app.extensions import db, init_extensions, jwt
from .routes.job import job_bp
from app.routes.addre_salary import addr_sal_bp
from app.routes.requirement import requirement_bp
from app.routes.worker import worker_bp
from app.routes.user_auth import auth_bp
from app.routes.tasks import task_bp
from app.error.error import register_error_handler, register_jwt_error_handler


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    env = os.getenv("FLASK_ENV", "development")

    if env == "development":
        app.config.from_object("config.Development")
    else:
        app.config.from_object("config.Test")

    init_extensions(app=app)

    register_error_handler(app)

    register_jwt_error_handler(jwt, app)

    if env == "development":
        with app.app_context():
            db.create_all()
            app.logger.info("Successfully connect to Postgres Database")

    app.register_blueprint(job_bp)
    app.register_blueprint(addr_sal_bp)
    app.register_blueprint(requirement_bp)
    app.register_blueprint(worker_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)

    return app
