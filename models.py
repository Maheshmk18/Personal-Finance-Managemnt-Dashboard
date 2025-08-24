from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, Numeric
from decimal import Decimal

# Mandatory for Replit Auth
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('SavingsGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='user', lazy=True, cascade='all, delete-orphan')

# Mandatory for Replit Auth
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key', 
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # checking, savings, credit, investment
    balance = db.Column(Numeric(12, 2), default=0)
    currency = db.Column(db.String(3), default='USD')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income, expense
    icon = db.Column(db.String(50), default='fas fa-tag')
    color = db.Column(db.String(7), default='#6c757d')
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    user_id = db.Column(db.String, db.ForeignKey('users.id'))  # NULL for system categories
    is_system = db.Column(db.Boolean, default=False)
    
    # Self-referencing relationship
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budgets = db.relationship('Budget', backref='category', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    amount = db.Column(Numeric(12, 2), nullable=False)
    description = db.Column(db.String(200))
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # income, expense, transfer
    payment_method = db.Column(db.String(20))  # cash, credit_card, debit_card, transfer
    tags = db.Column(db.Text)  # JSON string for tags
    notes = db.Column(db.Text)
    is_recurring = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(Numeric(12, 2), nullable=False)
    period = db.Column(db.String(10), default='monthly')  # monthly, yearly
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(Numeric(12, 2), nullable=False)
    current_amount = db.Column(Numeric(12, 2), default=0)
    target_date = db.Column(db.Date)
    description = db.Column(db.Text)
    is_achieved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(Numeric(12, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    frequency = db.Column(db.String(20), default='monthly')  # monthly, weekly, yearly, one-time
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_paid = db.Column(db.Boolean, default=False)
    auto_pay = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)


# Initialize system categories
def init_system_categories():
    """Initialize system categories if they don't exist"""
    system_categories = [
        # Expense categories
        {'name': 'Food & Dining', 'type': 'expense', 'icon': 'fas fa-utensils', 'color': '#fd7e14'},
        {'name': 'Transportation', 'type': 'expense', 'icon': 'fas fa-car', 'color': '#0d6efd'},
        {'name': 'Shopping', 'type': 'expense', 'icon': 'fas fa-shopping-bag', 'color': '#dc3545'},
        {'name': 'Entertainment', 'type': 'expense', 'icon': 'fas fa-film', 'color': '#6f42c1'},
        {'name': 'Bills & Utilities', 'type': 'expense', 'icon': 'fas fa-file-invoice', 'color': '#198754'},
        {'name': 'Healthcare', 'type': 'expense', 'icon': 'fas fa-heartbeat', 'color': '#20c997'},
        {'name': 'Travel', 'type': 'expense', 'icon': 'fas fa-plane', 'color': '#0dcaf0'},
        {'name': 'Education', 'type': 'expense', 'icon': 'fas fa-graduation-cap', 'color': '#ffc107'},
        {'name': 'Personal Care', 'type': 'expense', 'icon': 'fas fa-spa', 'color': '#d63384'},
        {'name': 'Home & Garden', 'type': 'expense', 'icon': 'fas fa-home', 'color': '#6c757d'},
        {'name': 'Other', 'type': 'expense', 'icon': 'fas fa-question', 'color': '#adb5bd'},
        
        # Income categories
        {'name': 'Salary', 'type': 'income', 'icon': 'fas fa-money-bill-wave', 'color': '#198754'},
        {'name': 'Freelance', 'type': 'income', 'icon': 'fas fa-laptop', 'color': '#20c997'},
        {'name': 'Investments', 'type': 'income', 'icon': 'fas fa-chart-line', 'color': '#0dcaf0'},
        {'name': 'Business', 'type': 'income', 'icon': 'fas fa-briefcase', 'color': '#fd7e14'},
        {'name': 'Other Income', 'type': 'income', 'icon': 'fas fa-plus-circle', 'color': '#ffc107'},
    ]
    
    for cat_data in system_categories:
        existing = Category.query.filter_by(name=cat_data['name'], is_system=True, user_id=None).first()
        if not existing:
            category = Category(
                name=cat_data['name'],
                type=cat_data['type'],
                icon=cat_data['icon'],
                color=cat_data['color'],
                is_system=True,
                user_id=None
            )
            db.session.add(category)
    
    db.session.commit()
