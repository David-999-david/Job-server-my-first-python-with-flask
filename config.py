import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

basedir = Path(__file__).parent
load_dotenv(basedir / '.env')


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dot-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', 1)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # SESSION_COOKIE_HITONLY = True
    # REMEMBER_COOKIE_HITONLY = True
    # SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE = False
    # REMEMBER_COOKIE_DURATION = timedelta(days=14)

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_SESSION_COOKIE = False
    JWT_COOKIE_CSRF_PROTECT = True

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    # 60 * 15
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    # 60 * 60 * 24 * 14

    OTP_HMAC_SECRET = os.getenv("OTP_HMAC_SECRET")


class Development(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO = True


class Test(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
