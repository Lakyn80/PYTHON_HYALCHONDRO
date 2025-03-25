from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file
from app.models import db, Product, Order, Customer
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import CustomerLoginForm, CustomerRegisterForm, CheckoutForm, ProfileUpdateForm
from flask_mail import Message
from .extensions import mail
from app.tokens import generate_reset_token, verify_reset_token
from app.email import send_reset_email
from app.utils.pdf_generator import generate_invoice_pdf

client_bp = Blueprint('client', __name__)

# ГЛАВНАЯ СТРАНИЦА
@client_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('client/landing_page.html', products=products)

@client_bp.route('/products')
def redirect_to_product():
    return redirect(url_for('client.product_detail', product_id=1))

# РЕГИСТРАЦИЯ
@client_bp.route('/register', methods=['GET', 'POST'])
def register_customer():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        existing_user = Customer.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Этот адрес электронной почты уже используется.', 'error')
            return redirect(url_for('client.register_customer'))
        hashed_password = generate_password_hash(form.password.data)
        new_customer = Customer(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        flash('Регистрация прошла успешно. Теперь вы можете войти.', 'success')
        return redirect(url_for('client.login_customer'))
    return render_template('client/register.html', form=form)

# ВХОД
@client_bp.route('/login', methods=['GET', 'POST'])
def login_customer():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['customer_logged_in'] = True
            session['customer_email'] = user.email
            session['customer_id'] = user.id
            flash('Вход выполнен успешно.', 'success')
            return redirect(url_for('client.index'))
        else:
            flash('Неверный логин или пароль.', 'danger')
    return render_template('client/login.html', form=form)

# ЗАПРОС НА СБРОС ПАРОЛЯ
@client_bp.route("/reset_password-request", methods=["POST"])
def reset_password_request():
    email = request.form.get("reset_email")
    if not email:
        flash("Email обязателен.", "error")
        return redirect(url_for("client.login_customer"))

    user = Customer.query.filter_by(email=email).first()
    if user:
        token = generate_reset_token(user)
        reset_link = url_for('client.reset_password', token=token, _external=True)
        send_reset_email(user.email, reset_link)
        flash("Ссылка для сброса пароля отправлена на вашу почту.", "success")
    else:
        flash("Пользователь с таким email не найден.", "error")
    return redirect(url_for("client.login_customer"))

# СБРОС ПАРОЛЯ
@client_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = verify_reset_token(token)
    if not user:
        flash('Недействительный или истекший токен.', 'error')
        return redirect(url_for('client.login_customer'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if not password or not confirm:
            flash('Все поля обязательны.', 'error')
            return redirect(request.url)

        if password != confirm:
            flash('Пароли не совпадают.', 'error')
            return redirect(request.url)

        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Пароль успешно изменён.', 'success')
        return redirect(url_for('client.login_customer'))

    return render_template('client/reset_password.html', token=token)

# ВЫХОД
@client_bp.route('/logout')
def logout_customer():
    session.clear()
    flash('Вы вышли из аккаунта.', 'success')
    return redirect(url_for('client.index'))

# ЗАКАЗЫ
@client_bp.route('/account/orders')
def customer_orders():
    if not session.get('customer_logged_in') or 'customer_id' not in session:
        flash('Пожалуйста, войдите в аккаунт, чтобы увидеть заказы.', 'warning')
        return redirect(url_for('client.login_customer'))
    orders = Order.query.filter_by(customer_id=session['customer_id']).order_by(Order.created_at.desc()).all()
    return render_template('client/customer_orders.html', orders=orders)

# ПОДРОБНОСТИ О ПРОДУКТЕ
@client_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('client/product.html', product=product)

# ДОБАВИТЬ В КОРЗИНУ
@client_bp.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not session.get('customer_logged_in'):
        flash('Пожалуйста, войдите в аккаунт, чтобы добавить товар.', 'warning')
        return redirect(url_for('client.login_customer'))

    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    session['cart'] = cart
    flash('Товар добавлен в корзину.', 'success')
    return redirect(url_for('client.cart'))

# КОРЗИНА
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

# ОБНОВИТЬ КОРЗИНУ
@client_bp.route('/update-cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', {})
    for key, value in request.form.items():
        if key.startswith("quantity_"):
            pid = key.split("_")[1]
            cart[pid] = max(1, int(value))
    session['cart'] = cart
    flash('Корзина обновлена.', 'success')
    return redirect(url_for('client.cart'))

# УДАЛИТЬ ИЗ КОРЗИНЫ
@client_bp.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Товар удалён из корзины.', 'success')
    return redirect(url_for('client.cart'))

# ОФОРМЛЕНИЕ ЗАКАЗА
@client_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not session.get('customer_logged_in'):
        flash('Войдите в аккаунт, чтобы оформить заказ.', 'warning')
        return redirect(url_for('client.login_customer'))

    cart = session.get('cart', {})
    if not cart:
        flash('Ваша корзина пуста.', 'error')
        return redirect(url_for('client.cart'))

    form = CheckoutForm()
    if form.validate_on_submit():
        orders = []
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
                orders.append(order)

        db.session.commit()

        invoice_pdf = generate_invoice_pdf(orders[0])
        send_order_email(form.email.data, form.name.data, invoice_pdf)

        session.pop('cart', None)
        flash('Заказ успешно оформлен.', 'success')
        return redirect(url_for('client.order_success'))

    return render_template('client/checkout.html', form=form)

# УСПЕШНЫЙ ЗАКАЗ
@client_bp.route('/order-success')
def order_success():
    return render_template('client/order_success.html')

# ОТПРАВКА ПИСЬМА С ПОДТВЕРЖДЕНИЕМ
def send_order_email(email, name, invoice_pdf):
    msg = Message("Подтверждение заказа", recipients=[email])
    msg.body = f"Здравствуйте, {name}!\n\nСпасибо за ваш заказ."

    msg.attach(
        filename="счёт-фактура.pdf",
        content_type="application/pdf",
        data=invoice_pdf.getvalue()
    )

    try:
        mail.send(msg)
        print("✅ Письмо с счётом отправлено")
    except Exception as e:
        print(f"❌ Ошибка при отправке письма: {e}")

# ПРОФИЛЬ КЛИЕНТА
@client_bp.route('/account/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('customer_logged_in'):
        flash("Пожалуйста, войдите в аккаунт для доступа к профилю.", "warning")
        return redirect(url_for('client.login_customer'))

    customer = Customer.query.get(session['customer_id'])
    form = ProfileUpdateForm(obj=customer)

    if form.validate_on_submit():
        customer.name = form.name.data
        customer.surname = form.surname.data
        customer.address = form.address.data
        customer.phone = form.phone.data

        db.session.commit()
        flash("Профиль обновлён.", "success")
        return redirect(url_for('client.profile'))

    return render_template('client/profile.html', customer=customer, form=form)
