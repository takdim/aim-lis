import os
from datetime import timedelta


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://user:password@localhost:3306/hukum_new",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_IDLE_TIMEOUT_MINUTES = max(_env_int("SESSION_IDLE_TIMEOUT_MINUTES", 120), 1)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_IDLE_TIMEOUT_MINUTES)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
