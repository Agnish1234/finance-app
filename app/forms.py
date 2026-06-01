from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TransactionForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    category = SelectField('Category', choices=[
        ('Food', 'Food'), ('Transport', 'Transport'), ('Entertainment', 'Entertainment'),
        ('Bills', 'Bills'), ('Shopping', 'Shopping'), ('Salary', 'Salary'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    type = SelectField('Type', choices=[('expense', 'Expense'), ('income', 'Income')], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Add Transaction')