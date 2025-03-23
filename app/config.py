import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tajny_klic')

    # ✅ Databáze
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:205800@localhost:5432/hyalchondro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Email server
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'artemodernoblaha@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'qxunfbtnyvefainm')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
