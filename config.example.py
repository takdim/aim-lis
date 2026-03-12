import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://user:password@localhost:3306/hukum_new",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
