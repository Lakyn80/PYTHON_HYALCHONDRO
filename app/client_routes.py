from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models import db, Product, Order, Customer
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import CustomerLoginForm, CustomerRegisterForm, CheckoutForm
from flask_mail import Message
from .extensions import mail
from app.forms import ProfileUpdateForm

client_bp = Blueprint('client', __name__)

# LANDING PAGE
@client_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('client/landing_page.html', products=products)

@client_bp.route('/products')
def redirect_to_product():
    return redirect(url_for('client.product_detail', product_id=1))


# REGISTRACE ZÁKAZNÍKA
@client_bp.route('/register', methods=['GET', 'POST'])
def register_customer():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        existing_user = Customer.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Tento email již existuje.', 'error')
            return redirect(url_for('client.register_customer'))
        hashed_password = generate_password_hash(form.password.data)
        new_customer = Customer(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        flash('Registrace proběhla úspěšně. Můžete se přihlásit.', 'success')
        return redirect(url_for('client.login_customer'))
    return render_template('client/register.html', form=form)

# PŘIHLÁŠENÍ ZÁKAZNÍKA
@client_bp.route('/login', methods=['GET', 'POST'])
def login_customer():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['customer_logged_in'] = True
            session['customer_email'] = user.email
            session['customer_id'] = user.id
            flash('Přihlášení úspěšné.', 'success')
            return redirect(url_for('client.index'))
        else:
            flash('Neplatné přihlašovací údaje.', 'danger')
    return render_template('client/login.html', form=form)

# ODHLÁŠENÍ
@client_bp.route('/logout')
def logout_customer():
    session.clear()
    flash('Odhlášení úspěšné.', 'success')
    return redirect(url_for('client.index'))

# OBJEDNÁVKY ZÁKAZNÍKA
@client_bp.route('/account/orders')
def customer_orders():
    if not session.get('customer_logged_in') or 'customer_id' not in session:
        flash('Pro zobrazení objednávek se musíte přihlásit.', 'warning')
        return redirect(url_for('client.login_customer'))
    orders = Order.query.filter_by(customer_id=session['customer_id']).order_by(Order.created_at.desc()).all()
    return render_template('client/customer_orders.html', orders=orders)

# DETAIL PRODUKTU
@client_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('client/product.html', product=product)

# PŘIDAT DO KOŠÍKU
@client_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session['cart'] = cart
    flash('Produkt byl přidán do košíku.', 'success')
    return redirect(url_for('client.cart'))

# ZOBRAZENÍ KOŠÍKU
@client_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    items = []
    total = 0
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal = qty * product.price
            items.append({'product': product, 'quantity': qty, 'total': subtotal})
            total += subtotal
    return render_template('client/cart.html', products=items, total_price=total)

# AKTUALIZACE KOŠÍKU
@client_bp.route('/update-cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', {})
    for key, value in request.form.items():
        if key.startswith("quantity_"):
            pid = key.split("_")[1]
            cart[pid] = max(1, int(value))
    session['cart'] = cart
    flash('Košík byl aktualizován.', 'success')
    return redirect(url_for('client.cart'))

# ODEBRÁNÍ Z KOŠÍKU
@client_bp.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Produkt byl odebrán z košíku.', 'success')
    return redirect(url_for('client.cart'))

# CHECKOUT
@client_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Košík je prázdný.', 'error')
        return redirect(url_for('client.cart'))
    form = CheckoutForm()
    if form.validate_on_submit():
        for pid, qty in cart.items():
            product = Product.query.get(int(pid))
            if product:
                order = Order(
                    name=form.name.data,
                    email=form.email.data,
                    address=form.address.data,
                    product_id=product.id,
                    quantity=qty,
                    customer_id=session.get('customer_id')
                )
                db.session.add(order)
        db.session.commit()
        send_order_email(email=form.email.data, name=form.name.data)
        session.pop('cart', None)
        flash('Objednávka úspěšně dokončena.', 'success')
        return redirect(url_for('client.order_success'))
    return render_template('client/checkout.html', form=form)

# OBJEDNÁVKA DOKONČENA
@client_bp.route('/order-success')
def order_success():
    return render_template('client/order_success.html')

# EMAIL FUNKCE
def send_order_email(email, name):
    msg = Message("Potvrzení objednávky", recipients=[email])
    msg.body = f"Dobrý den {name},\n\nDěkujeme za Vaši objednávku."
    try:
        mail.send(msg)
        print("✅ Email odeslán")
    except Exception as e:
        print(f"❌ Email chyba: {e}")



from app.forms import ProfileUpdateForm

@client_bp.route('/account/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('customer_logged_in'):
        flash("Musíte se přihlásit pro zobrazení profilu.", "warning")
        return redirect(url_for('client.login_customer'))

    customer = Customer.query.get(session['customer_id'])
    form = ProfileUpdateForm(obj=customer)

    if form.validate_on_submit():
        customer.name = form.name.data
        customer.surname = form.surname.data
        customer.address = form.address.data
        customer.phone = form.phone.data

        db.session.commit()
        flash("Profil byl aktualizován.", "success")
        return redirect(url_for('client.profile'))

    return render_template('client/profile.html', customer=customer, form=form)


