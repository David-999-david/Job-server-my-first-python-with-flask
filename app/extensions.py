from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
seralizer: URLSafeTimedSerializer = None


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app)
    mail.init_app(app)

    global seralizer
    seralizer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"],
        salt="email_confirm_salt"
    )
