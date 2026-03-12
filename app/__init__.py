import getpass

import click
from flask import Flask
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

from .models import db
from .models import User

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    @app.cli.command("init-admin")
    def init_admin():
        """Create the first admin user via CLI."""
        if User.query.first() is not None:
            click.echo("Admin sudah ada. Tidak ada perubahan.")
            return

        username = click.prompt("Username", type=str)
        realname = click.prompt("Nama lengkap", type=str)
        password = getpass.getpass("Password: ")

        if not username or not realname or not password:
            click.echo("Semua field wajib diisi.")
            return

        user = User(
            username=username.strip(),
            realname=realname.strip(),
            passwd=generate_password_hash(password),
            groups="admin",
        )
        db.session.add(user)
        db.session.commit()
        click.echo("Admin pertama berhasil dibuat.")

    return app
