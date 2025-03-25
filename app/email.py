from flask_mail import Message
from .extensions import mail

def send_reset_email(to_email, reset_link):
    msg = Message("Obnova hesla", recipients=[to_email])
    msg.body = f"""Ahoj,

Pro obnovu hesla klikni na následující odkaz:

{reset_link}

Pokud jste o obnovu hesla nežádali, tento email ignorujte.
"""
    try:
        mail.send(msg)
    except Exception as e:
        print(f"❌ Chyba při odesílání emailu: {e}")
