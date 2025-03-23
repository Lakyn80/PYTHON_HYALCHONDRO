from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, TextAreaField,
    IntegerField, FloatField, FileField, EmailField, SelectField
)
from wtforms.validators import (
    DataRequired, EqualTo, Email, Length, NumberRange, Optional
)


class AdminLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    submit = SubmitField("Přihlásit")


class AdminRegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Heslo", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Potvrzení hesla",
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("Registrovat")


class ProductForm(FlaskForm):
    name = StringField("Název produktu", validators=[DataRequired()])
    description = TextAreaField("Popis", validators=[DataRequired()])
    price = FloatField("Cena", validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Počet kusů", validators=[DataRequired(), NumberRange(min=0)])
    image = FileField("Obrázek", validators=[Optional()])
    submit = SubmitField("Uložit")


class CustomerRegisterForm(FlaskForm):
    name = StringField("Jméno", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Heslo", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Potvrzení hesla",
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField("Registrovat")


class CustomerLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Heslo", validators=[DataRequired()])
    submit = SubmitField("Přihlásit")


class CheckoutForm(FlaskForm):
    name = StringField("Jméno a příjmení", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    address = TextAreaField("Adresa", validators=[DataRequired()])
    payment_method = SelectField(
        "Způsob platby",
        choices=[("card", "Karta"), ("cash", "Dobírka")],
        validators=[DataRequired()]
    )
    submit = SubmitField("Zaplatit")
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Optional

class ProfileUpdateForm(FlaskForm):
    name = StringField('Jméno')
    surname = StringField('Příjmení')
    email = StringField('Email')
    address = StringField('Adresa')
    phone = StringField('Telefon')
    submit = SubmitField('Uložit změny')

