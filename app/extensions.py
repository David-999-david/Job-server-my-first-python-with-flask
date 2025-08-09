from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
# from flask_login import LoginManager
# from flask_wtf import CSRFProtect
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
seralizer: URLSafeTimedSerializer = None
# login = LoginManager()
# csrf = CSRFProtect()
jwt = JWTManager()


def init_extensions(app):
    db.init_app(app)
    migrate.init_app(app)
    mail.init_app(app)
    # login.init_app(app)
    # csrf.init_app(app)
    jwt.init_app(app)

    global seralizer
    seralizer = URLSafeTimedSerializer(
        app.config["SECRET_KEY"],
        salt="email_confirm_salt"
    )
