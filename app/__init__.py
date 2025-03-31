import os
from flask import Flask
from dotenv import load_dotenv
from app.config import Config  # Update import path
from .extensions import db, mail, migrate
from app.admin_routes import admin_bp
from app.client_routes import client_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializace rozšíření
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Blueprinty
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)

    # 💡 Debug výstup databáze
    print("🧠 DATABASE:", app.config['SQLALCHEMY_DATABASE_URI'])

    # CLI příkazy (jako `flask db-test`)
    register_commands(app)

    return app


# ✅ CLI: Test DB připojení
def register_commands(app):
    @app.cli.command("db-test")
    def db_test():
        from app.models import Order
        try:
            print("🔄 Zkouším dotaz na Order.query.first()...")
            order = Order.query.first()
            if order:
                print(f"✅ Načtena objednávka ID {order.id}, stav: {order.status}")
            else:
                print("⚠️ Žádné objednávky zatím nejsou v databázi.")
        except Exception as e:
            print("❌ Chyba při dotazu na databázi:")
            print(e)
