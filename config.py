import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tajny_klic')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:heslo@localhost:5432/hyalchondro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'placeholder@example.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'placeholderpassword')
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
