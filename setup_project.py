# Vygenerování kompletního setup_project.py se všemi potřebnými soubory a obsahem
import os

# Obsah jednotlivých souborů jako textové proměnné

run_py = """
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
"""

config_py = """
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tajny_klic')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:heslo@localhost:5432/hyalchondro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""

init_py = """
import os
from flask import Flask
from dotenv import load_dotenv
from .models import db
from .routes import main
from config import Config

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.secret_key = os.getenv("SECRET_KEY", "fallback_klic_kdyz_env_chybi")

    with app.app_context():
        db.create_all()

    app.register_blueprint(main)

    return app
"""

models_py = """
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
"""

routes_py = """
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, AdminUser

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('client/landing_page.html')

@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = AdminUser.query.filter_by(username=username, password=password).first()
        if user:
            flash('Přihlášení úspěšné!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Neplatné přihlašovací údaje', 'error')
            return redirect(url_for('main.admin_login'))

    return render_template('admin/login.html')

@main.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Hesla se neshodují.', 'error')
            return redirect(url_for('main.admin_register'))

        if AdminUser.query.filter_by(username=username).first():
            flash('Uživatel už existuje!', 'error')
            return redirect(url_for('main.admin_register'))

        new_user = AdminUser(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrace úspěšná!', 'success')
        return redirect(url_for('main.admin_login'))

    return render_template('admin/register.html')

@main.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')
"""

# Vytvoření složek
os.makedirs("app", exist_ok=True)

# Zápis souborů
with open("run.py", "w", encoding="utf-8") as f:
    f.write(run_py.strip())

with open("config.py", "w", encoding="utf-8") as f:
    f.write(config_py.strip())

with open("app/__init__.py", "w", encoding="utf-8") as f:
    f.write(init_py.strip())

with open("app/models.py", "w", encoding="utf-8") as f:
    f.write(models_py.strip())

with open("app/routes.py", "w", encoding="utf-8") as f:
    f.write(routes_py.strip())

