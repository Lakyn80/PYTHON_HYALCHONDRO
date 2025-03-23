from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, AdminUser, Product, Order
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from app.forms import AdminLoginForm, AdminRegisterForm, ProductForm
from wtforms.validators import Email
from app.models import Customer


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = os.path.join('app', 'static', 'product-images')

# LOGIN
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['admin_logged_in'] = True
            flash('Přihlášení úspěšné.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
        flash('Neplatné přihlašovací údaje.', 'error')
    return render_template('admin/login.html', form=form)

# LOGOUT
@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Odhlášení proběhlo úspěšně.', 'success')
    return redirect(url_for('admin.admin_login'))

# REGISTRACE
@admin_bp.route('/register', methods=['GET', 'POST'])
def admin_register():
    form = AdminRegisterForm()
    if form.validate_on_submit():
        if AdminUser.query.filter_by(email=form.email.data).first():
            flash('Email již existuje.', 'error')
            return redirect(url_for('admin.admin_register'))
        hashed = generate_password_hash(form.password.data)
        db.session.add(AdminUser(email=form.email.data, password=hashed))
        db.session.commit()
        flash('Registrace úspěšná.', 'success')
        return redirect(url_for('admin.admin_login'))
    return render_template('admin/register.html', form=form)

# DASHBOARD
@admin_bp.route('/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

# OBJEDNÁVKY
@admin_bp.route('/orders')
def view_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

# PŘIDAT PRODUKT
@admin_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    form = ProductForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = None
        if image:
            filename = secure_filename(image.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(path)
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            image_filename=filename
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Produkt byl přidán.', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/add_product.html', form=form)

# UPRAVIT PRODUKT
@admin_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            path = os.path.join(UPLOAD_FOLDER, filename)
            form.image.data.save(path)
            product.image_filename = filename
        db.session.commit()
        flash('Produkt upraven.', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/edit_product.html', form=form, product=product)

# SMAZAT PRODUKT
@admin_bp.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produkt byl smazán.', 'success')
    return redirect(url_for('admin.admin_dashboard'))
