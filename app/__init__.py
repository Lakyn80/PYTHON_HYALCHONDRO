import os
from flask import Flask
from dotenv import load_dotenv
from .models import db
from .extensions import db, mail, migrate
from app.admin_routes import admin_bp
from app.client_routes import client_bp
from config import Config

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializace rozšíření
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Vytvoření DB tabulek (jen výjimečně používej db.create_all)
    with app.app_context():
        # db.create_all() ← pokud nemáš migrace – jinak používej flask db upgrade
        pass

    # Blueprinty
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)

    return app
