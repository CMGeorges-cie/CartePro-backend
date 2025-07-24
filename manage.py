# manage.py
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import click

app = create_app()
cli = FlaskGroup(app)

@app.cli.command("create-db")
def create_db():
    db.create_all()
    click.echo("✅ Base de données créée.")

@app.cli.command("drop-db")
def drop_db():
    db.drop_all()
    click.echo("🗑️ Base de données supprimée.")

@app.cli.command("seed-admin")
def seed_admin():
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=generate_password_hash("adminpass"),
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
    click.echo("👑 Admin ajouté.")

if __name__ == "__main__":
    cli()
