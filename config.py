import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).parent
load_dotenv(basedir / '.env')


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dot-key")
    SQLALCHEMY_TRACK_MODIFICATION = False


class Development(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_ECHO = True


class Test(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory"
    TESTING = True
