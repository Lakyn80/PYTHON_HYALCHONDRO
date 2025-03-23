from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from .models import db, AdminUser, Product
from werkzeug.utils import secure_filename
import os
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from .extensions import mail

main = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join('app', 'static', 'product-images')

# ----------------- TOKEN GENERATION -----------------
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        return serializer.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None

# ----------------- HOME -----------------
@main.route('/')
def index():
    return render_template('client/landing_page.html')

# ----------------- ADMIN LOGIN -----------------
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = AdminUser.query.filter_by(email=email, password=password).first()
        if user:
            session['admin_logged_in'] = True
            flash('Přihlášení úspěšné!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Neplatné přihlašovací údaje', 'error')

    return render_template('admin/login.html')

# ----------------- ADMIN LOGOUT -----------------
@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Byl jste odhlášen.', 'success')
    return redirect(url_for('main.admin_login'))

# ----------------- ADMIN REGISTER -----------------
@main.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Hesla se neshodují.', 'error')
            return redirect(url_for('main.admin_register'))

        if AdminUser.query.filter_by(email=email).first():
            flash('Uživatel s tímto e-mailem už existuje!', 'error')
            return redirect(url_for('main.admin_register'))

        new_user = AdminUser(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrace úspěšná!', 'success')
        return redirect(url_for('main.admin_login'))

    return render_template('admin/register.html')

# ----------------- ADMIN DASHBOARD -----------------
@main.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Přístup pouze pro přihlášené administrátory.', 'error')
        return redirect(url_for('main.admin_login'))

    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

# ----------------- ADD PRODUCT -----------------
@main.route('/admin/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))

        image = request.files.get('image')
        image_filename = None

        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(image_path)

        new_product = Product(
            name=name,
            description=description,
            price=price,
            image_filename=image_filename,
            stock=stock
        )
        db.session.add(new_product)
        db.session.commit()

        flash('Produkt úspěšně přidán.', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('admin/add_product.html')

# ----------------- EDIT PRODUCT -----------------
@main.route('/admin/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))

        image = request.files.get('image')
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, image_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
            product.image_filename = image_filename

        db.session.commit()
        flash('Produkt upraven.', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('admin/edit_product.html', product=product)

# ----------------- DELETE PRODUCT -----------------
@main.route('/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produkt smazán.', 'success')
    return redirect(url_for('main.admin_dashboard'))

# ----------------- FORGOT PASSWORD -----------------
@main.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = AdminUser.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(email)
            reset_link = url_for('main.reset_password', token=token, _external=True)

            msg = Message('Reset hesla – Hyalchondro Admin',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f'Odkaz na reset hesla: {reset_link}'

            try:
                mail.send(msg)
                flash('Resetovací odkaz byl odeslán na e-mail.', 'success')
            except Exception as e:
                print(f"❌ Chyba při odesílání emailu: {e}")
                flash('Chyba při odesílání e-mailu. Zkontroluj konfiguraci.', 'error')
        else:
            flash('Uživatel s tímto e-mailem neexistuje.', 'error')

    return render_template('admin/forgot_password.html')

# ----------------- RESET PASSWORD -----------------
@main.route('/admin/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Neplatný nebo expirovaný odkaz.', 'error')
        return redirect(url_for('main.admin_login'))

    user = AdminUser.query.filter_by(email=email).first()
    if not user:
        flash('Uživatel neexistuje.', 'error')
        return redirect(url_for('main.admin_login'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Hesla se neshodují.', 'error')
            return redirect(url_for('main.reset_password', token=token))

        user.password = new_password
        db.session.commit()
        flash('Heslo bylo úspěšně změněno.', 'success')
        return redirect(url_for('main.admin_login'))

    return render_template('admin/reset_password.html', token=token)
