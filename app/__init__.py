from flask import Flask
import os
from app.extensions import db, migrate
from .routes.job import job_bp
from app.routes.addre_salary import addr_sal_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    env = os.getenv("FLASK_ENV", "development")

    if env == "development":
        app.config.from_object("config.Development")
    else:
        app.config.from_object("config.Test")

    db.init_app(app)

    migrate.init_app(app, db)

    if env == "development":
        with app.app_context():
            db.create_all()
            app.logger.info("Successfully connect to Postgres Database")

    app.register_blueprint(job_bp)
    app.register_blueprint(addr_sal_bp)

    return app
