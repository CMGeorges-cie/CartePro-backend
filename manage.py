# manage.py
from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import click
import os

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
    username = os.environ.get("ADMIN_USERNAME") or click.prompt("Nom d'utilisateur admin")
    email = os.environ.get("ADMIN_EMAIL") or click.prompt("Courriel admin")
    password = os.environ.get("ADMIN_PASSWORD") or click.prompt("Mot de passe admin", hide_input=True, confirmation_prompt=True)
    if len(password) < 8:
        click.echo("❌ Le mot de passe doit contenir au moins 8 caractères.")
        return
    admin = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="admin",
        is_admin=True,
    )
    db.session.add(admin)
    db.session.commit()
    click.echo(f"👑 Admin '{username}' ajouté.")

if __name__ == "__main__":
    cli()
