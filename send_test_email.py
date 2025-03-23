from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# načti .env soubor
load_dotenv()

# inicializuj Flask app
app = Flask(__name__)

# konfigurace mailu
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'false').lower() in ['true', '1', 'yes']
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() in ['true', '1', 'yes']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

# odeslání testovacího e-mailu
with app.app_context():
    try:
        msg = Message(subject='Test Email',
                      recipients=['artemodernoblaha@gmail.com'],
                      body='Toto je testovací zpráva – Hyalchondro')
        mail.send(msg)
        print("✅ Email byl úspěšně odeslán!")
    except Exception as e:
        print(f"❌ Chyba při odesílání emailu: {e}")
