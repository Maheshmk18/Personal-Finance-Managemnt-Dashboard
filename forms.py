from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, TextAreaField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from decimal import Decimal

class AccountForm(FlaskForm):
    name = StringField('Account Name', validators=[DataRequired(), Length(min=1, max=100)])
    account_type = SelectField('Account Type', choices=[
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'), 
        ('credit', 'Credit Card'),
        ('investment', 'Investment Account')
    ], validators=[DataRequired()])
    balance = DecimalField('Initial Balance', validators=[DataRequired()], default=Decimal('0'))
    currency = SelectField('Currency', choices=[('USD', 'USD')], default='USD')

class TransactionForm(FlaskForm):
    account_id = SelectField('Account', coerce=int, validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    transaction_type = SelectField('Type', choices=[
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('transfer', 'Transfer')
    ], validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    description = StringField('Description', validators=[Length(max=200)])
    transaction_date = DateField('Date', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check')
    ])
    notes = TextAreaField('Notes', validators=[Length(max=500)])
    tags = StringField('Tags (comma-separated)', validators=[Length(max=200)])

class BudgetForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Budget Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    period = SelectField('Period', choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], default='monthly', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])

class SavingsGoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired(), Length(min=1, max=100)])
    target_amount = DecimalField('Target Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    target_date = DateField('Target Date', validators=[Optional()])
    description = TextAreaField('Description', validators=[Length(max=500)])

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=50)])
    type = SelectField('Type', choices=[
        ('income', 'Income'),
        ('expense', 'Expense')
    ], validators=[DataRequired()])
    icon = StringField('Icon Class', default='fas fa-tag')
    color = StringField('Color', default='#6c757d')
    parent_category_id = SelectField('Parent Category', coerce=int, validators=[Optional()])

class BillForm(FlaskForm):
    name = StringField('Bill Name', validators=[DataRequired(), Length(min=1, max=100)])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    due_date = DateField('Due Date', validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly'),
        ('one-time', 'One Time')
    ], default='monthly', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    auto_pay = BooleanField('Auto Pay')

    notes = TextAreaField('Notes', validators=[Length(max=500)])
