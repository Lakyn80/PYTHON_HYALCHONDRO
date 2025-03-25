from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_reset_token(user, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'user_id': user.id})

def verify_reset_token(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)
    except Exception:
        return None

    from app.models import Customer
    return Customer.query.get(data['user_id'])
