import os
import matplotlib
matplotlib.use('Agg')

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import db, AdminUser, Product, Order
from app.forms import AdminLoginForm, AdminRegisterForm, ProductForm
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime

EXPORT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'exports')
os.makedirs(EXPORT_FOLDER, exist_ok=True)

csv_path = os.path.join(EXPORT_FOLDER, 'orders_export.csv')
excel_path = os.path.join(EXPORT_FOLDER, 'orders_export.xlsx')
pdf_path = os.path.join(EXPORT_FOLDER, 'orders_export.pdf')

UPLOAD_FOLDER = os.path.join('app', 'static', 'product-images')

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# LOGIN
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = AdminUser.query.filter_by(email=form.email.data).first()
        if admin and check_password_hash(admin.password, form.password.data):
            session['admin_logged_in'] = True
            session['admin_email'] = admin.email
            flash('Přihlášení úspěšné.', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Neplatné přihlašovací údaje.', 'error')
    return render_template('admin/login.html', form=form)

# LOGOUT
@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    flash('Odhlášení proběhlo úspěšně.', 'success')
    return redirect(url_for('admin.login'))

# REGISTRACE
@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = AdminRegisterForm()
    if form.validate_on_submit():
        if AdminUser.query.filter_by(email=form.email.data).first():
            flash('Email již existuje.', 'error')
            return redirect(url_for('admin.register'))
        hashed = generate_password_hash(form.password.data)
        admin = AdminUser(email=form.email.data, password=hashed)
        db.session.add(admin)
        db.session.commit()
        flash('Registrace úspěšná.', 'success')
        return redirect(url_for('admin.login'))
    return render_template('admin/register.html', form=form)

# DASHBOARD
@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    products = Product.query.all()
    return render_template('admin/dashboard.html', products=products)

# OBJEDNÁVKY
@admin_bp.route('/orders')
def orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    orders = Order.query.filter_by(is_visible=True).order_by(Order.created_at.desc()).all()  # ✅
    return render_template('admin/orders.html', orders=orders)



# ZMĚNA STAVU OBJEDNÁVKY (API AJAX)
@admin_bp.route('/api/update-order-status', methods=['POST'])
def api_update_order_status():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Neautorizováno"}), 403

    data = request.get_json()
    order_id = data.get("order_id")
    new_status = data.get("status")

    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "message": "Objednávka nenalezena"}), 404

    order.status = new_status
    db.session.commit()
    return jsonify({"success": True, "message": f"Stav změněn na {new_status}"})

# === PRODUKTY ===
@admin_bp.route('/products')
def products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin_bp.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    form = ProductForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = None
        if image:
            filename = secure_filename(image.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            image_filename=filename
        )
        db.session.add(product)
        db.session.commit()
        flash('Produkt přidán.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_product.html', form=form)

@admin_bp.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        form.populate_obj(product)
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            form.image.data.save(os.path.join(UPLOAD_FOLDER, filename))
            product.image_filename = filename
        db.session.commit()
        flash('Produkt upraven.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_product.html', form=form, product=product)

@admin_bp.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produkt smazán.', 'success')
    return redirect(url_for('admin.dashboard'))

# EXPORT OBJEDNÁVEK
@admin_bp.route('/export-orders')
def export_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    # ✅ Smažeme staré soubory, pokud existují
    for path in [csv_path, excel_path, pdf_path]:
        if os.path.exists(path):
            os.remove(path)

    orders = Order.query.order_by(Order.created_at.desc()).all()
    data = []

    for order in orders:
        print(f"🧾 Objednávka {order.id} – status: {order.status}")  # 🔍 konzolová kontrola
        data.append({
            "ID": order.id,
            "Číslo objednávky": f"ORD{order.id:03}",
            "Zákazník": order.name,
            "Email": order.email,
            "Adresa": order.address,
            "Produkt": order.product.name if order.product else "Neznámý produkt",
            "Množství": order.quantity,
            "Datum": order.created_at.strftime("%Y-%m-%d"),
            "Číslo faktury": f"F{order.id:03}",
            "Stav": str(order.status) if order.status else "Neuvedeno"
        })

    df = pd.DataFrame(data)

    # ✅ Uložíme CSV a Excel
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)

    # ✅ Vygenerujeme PDF
    fig, ax = plt.subplots(figsize=(18, len(df) * 0.5 + 2))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.2)

    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    flash("✅ Exporty CSV, Excel a PDF byly úspěšně vygenerovány.", "success")
    return redirect(url_for('admin.orders'))


@admin_bp.route('/export-orders/<format>', methods=['POST'])
def export_orders_route(format):
    export_orders()  # ⚠️ Pozor – tohle přegeneruje všechny soubory

    file_map = {
        'csv': csv_path,
        'excel': excel_path,
        'pdf': pdf_path
    }

    file_to_send = file_map.get(format)
    if file_to_send and os.path.exists(file_to_send):
        return send_file(file_to_send, as_attachment=True)
    else:
        flash("❌ Soubor nelze stáhnout. Export selhal nebo neexistuje.", "error")
        return redirect(url_for("admin.orders"))
    

@admin_bp.route('/api/hide-order', methods=['POST'])
def api_hide_order():
    data = request.get_json()
    order_id = data.get("order_id")
    order = Order.query.get(order_id)
    if order:
        order.is_visible = False
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 404

