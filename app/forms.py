from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    IntegerField, FloatField, FileField, EmailField, SelectField
)
from wtforms.validators import (
    DataRequired, EqualTo, Email, Length, NumberRange, Optional
)


class AdminLoginForm(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class AdminRegisterForm(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Подтвердите пароль",
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("Зарегистрироваться")


class ProductForm(FlaskForm):
    name = StringField("Название продукта", validators=[DataRequired()])
    description = TextAreaField("Описание", validators=[DataRequired()])
    price = FloatField("Цена", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Количество", validators=[DataRequired(), NumberRange(min=0)])
    image = FileField("Изображение", validators=[Optional()])
    submit = SubmitField("Сохранить")


class CustomerRegisterForm(FlaskForm):
    name = StringField("Имя", validators=[DataRequired()])
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Подтвердите пароль",
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("Зарегистрироваться")


class CustomerLoginForm(FlaskForm):
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class CheckoutForm(FlaskForm):
    name = StringField("Имя и фамилия", validators=[DataRequired()])
    email = EmailField("Электронная почта", validators=[DataRequired(), Email()])
    address = TextAreaField("Адрес доставки", validators=[DataRequired()])
    payment_method = SelectField(
        "Способ оплаты",
        choices=[("card", "Картой"), ("cash", "Наложенный платеж")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Оплатить")


class ProfileUpdateForm(FlaskForm):
    name = StringField('Имя')
    surname = StringField('Фамилия')
    email = StringField('Электронная почта')
    address = StringField('Адрес')
    phone = StringField('Телефон')
    submit = SubmitField('Сохранить изменения')
