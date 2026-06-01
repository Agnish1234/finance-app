from flask_login import UserMixin
from . import db, login_manager

# This function is required by Flask-Login to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """User table: stores email and password hash."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    # Relationship: one user has many transactions
    transactions = db.relationship('Transaction', backref='owner', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Transaction(db.Model):
    """Transaction table: each record is an income or expense."""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))
    
    # Foreign key linking to the user who owns this transaction
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Transaction {self.type} {self.amount}>'