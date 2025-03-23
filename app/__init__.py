from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from config import Config
from .extensions import db, mail

# ✅ Načti .env proměnné
load_dotenv()

def create_app():
    app = Flask(__name__)

    # ✅ Načti konfiguraci
    app.config.from_object(Config)

    # ✅ Inicializace rozšíření
    db.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    # ✅ Registrace blueprintů
    from .routes import main
    app.register_blueprint(main)

    return app
