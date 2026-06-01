from flask import render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from io import StringIO, BytesIO
import csv

from . import db
from .models import User, Transaction
from .forms import RegistrationForm, LoginForm, TransactionForm

# Create a Blueprint to group routes
from flask import Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page: shows login/register links."""
    return render_template('index.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('main.login'))
        # Create new user
        hashed_password = generate_password_hash(form.password.data)
        user = User(email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = TransactionForm()
    if form.validate_on_submit():
        # Add new transaction
        transaction = Transaction(
            amount=form.amount.data,
            category=form.category.data,
            type=form.type.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added!', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Get filter parameters from request (optional)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    type_filter = request.args.get('type')
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    if type_filter and type_filter in ['income', 'expense']:
        query = query.filter_by(type=type_filter)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    # Calculate totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expense = sum(t.amount for t in transactions if t.type == 'expense')
    balance = total_income - total_expense
    
    # Prepare data for chart (last 30 days)
    from collections import defaultdict
    import calendar
    # Simple: group by date
    daily_net = defaultdict(float)
    for t in transactions:
        daily_net[t.date] += t.amount if t.type == 'income' else -t.amount
    # Sort dates for chart
    sorted_dates = sorted(daily_net.keys())
    chart_data = {
        'labels': [d.strftime('%Y-%m-%d') for d in sorted_dates[-30:]],
        'values': [daily_net[d] for d in sorted_dates[-30:]]
    }
    
    return render_template('dashboard.html', 
                           form=form, 
                           transactions=transactions,
                           total_income=total_income,
                           total_expense=total_expense,
                           balance=balance,
                           chart_data=chart_data)

@main_bp.route('/export/csv')
@login_required
def export_csv():
    """Export user's transactions as a CSV file."""
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    
    # Create a string buffer (like a file in memory)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description'])
    for t in transactions:
        writer.writerow([t.date, t.type, t.category, t.amount, t.description])
    
    # Convert to bytes and send as downloadable file
    output.seek(0)
    return send_file(
        BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'transactions_{datetime.now().strftime("%Y%m%d")}.csv'
    )

# API endpoint for JSON (for mobile apps or AJAX)
@main_bp.route('/api/transactions', methods=['GET'])
@login_required
def api_transactions():
    """Return transactions as JSON."""
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': t.id,
        'amount': t.amount,
        'category': t.category,
        'type': t.type,
        'date': t.date.isoformat(),
        'description': t.description
    } for t in transactions])