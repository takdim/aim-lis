import getpass

import click
from flask import Flask
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
import json

from .models import db
from .models import User
from .models import UserGroup

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_privileges():
        from flask import session

        uid = session.get("user_id")
        if not uid:
            return {"has_priv": lambda *args: False}
        user = User.query.get(uid)
        if not user:
            return {"has_priv": lambda *args: False}
        groups = [g.strip() for g in (user.groups or "").split(",") if g.strip()]
        if any(g.lower() == "admin" for g in groups):
            return {"has_priv": lambda *args: True}
        group_rows = UserGroup.query.filter(UserGroup.group_name.in_(groups)).all() if groups else []
        privs: set[str] = set()
        for row in group_rows:
            try:
                items = json.loads(row.privileges) if row.privileges else []
            except Exception:
                items = []
            for item in items:
                privs.add(str(item))

        def has_priv(*keys: str):
            return any(k in privs for k in keys)

        return {"has_priv": has_priv}

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
