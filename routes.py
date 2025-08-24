from flask import session, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from datetime import datetime, date, timedelta
from decimal import Decimal
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import Account, Transaction, Category, Budget, SavingsGoal, Bill, init_system_categories
from forms import AccountForm, TransactionForm, BudgetForm, SavingsGoalForm, CategoryForm, BillForm
from utils import *

# Register Replit Auth blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Initialize system categories on first run
with app.app_context():
    init_system_categories()

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    """Landing page for logged out users, dashboard for logged in users"""
    if not current_user.is_authenticated:
        return render_template('landing.html')
    
    # Dashboard data for logged in users
    user_id = current_user.id
    
    # Get user accounts with balances
    accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
    account_data = []
    total_balance = Decimal('0')
    
    for account in accounts:
        balance = get_account_balance(account.id)
        account.balance = balance  # Update balance
        account_data.append(account)
        if account.account_type in ['checking', 'savings', 'investment']:
            total_balance += balance
        elif account.account_type == 'credit':
            total_balance -= abs(balance)
    
    # Get recent transactions
    recent_transactions = get_recent_transactions(user_id)
    
    # Get monthly spending by category
    monthly_spending = get_monthly_spending_by_category(user_id)
    
    # Get budget progress
    budget_progress = get_budget_progress(user_id)
    
    # Get savings goals
    savings_goals = get_savings_goals_progress(user_id)
    
    # Get upcoming bills
    upcoming_bills = get_upcoming_bills(user_id)
    
    # Calculate financial health score
    health_score = get_financial_health_score(user_id)
    
    # Get net worth data
    net_worth_data = calculate_net_worth(user_id)
    
    return render_template('dashboard.html',
                         accounts=account_data,
                         total_balance=total_balance,
                         recent_transactions=recent_transactions,
                         monthly_spending=monthly_spending,
                         budget_progress=budget_progress,
                         savings_goals=savings_goals,
                         upcoming_bills=upcoming_bills,
                         health_score=health_score,
                         net_worth_data=net_worth_data)

@app.route('/accounts')
@require_login
def accounts():
    """Account management page"""
    user_accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Update balances
    for account in user_accounts:
        account.balance = get_account_balance(account.id)
    
    return render_template('accounts.html', accounts=user_accounts)

@app.route('/accounts/add', methods=['GET', 'POST'])
@require_login
def add_account():
    """Add new account"""
    form = AccountForm()
    
    if form.validate_on_submit():
        account = Account(
            user_id=current_user.id,
            name=form.name.data,
            account_type=form.account_type.data,
            balance=form.balance.data,
            currency=form.currency.data
        )
        db.session.add(account)
        db.session.commit()
        flash('Account added successfully!', 'success')
        return redirect(url_for('accounts'))
    
    return render_template('forms/account_form.html', form=form, title='Add Account')

@app.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_account(account_id):
    """Edit account"""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    form = AccountForm(obj=account)
    
    if form.validate_on_submit():
        account.name = form.name.data
        account.account_type = form.account_type.data
        account.currency = form.currency.data
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('accounts'))
    
    return render_template('forms/account_form.html', form=form, title='Edit Account')

@app.route('/accounts/<int:account_id>/delete', methods=['POST'])
@require_login
def delete_account(account_id):
    """Delete account"""
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first_or_404()
    account.is_active = False
    db.session.commit()
    flash('Account deactivated successfully!', 'success')
    return redirect(url_for('accounts'))

@app.route('/transactions')
@require_login
def transactions():
    """Transaction management page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get filters
    account_id = request.args.get('account_id', type=int)
    category_id = request.args.get('category_id', type=int)
    transaction_type = request.args.get('type')
    
    # Build query
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    if account_id:
        query = query.filter_by(account_id=account_id)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    
    # Paginate
    transactions_paginated = query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.created_at.desc()
    ).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get filter options
    user_accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    user_categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.is_system == True)
    ).all()
    
    return render_template('transactions.html',
                         transactions=transactions_paginated,
                         accounts=user_accounts,
                         categories=user_categories)

@app.route('/transactions/add', methods=['GET', 'POST'])
@require_login
def add_transaction():
    """Add new transaction"""
    form = TransactionForm()
    
    # Populate choices
    user_accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    form.account_id.choices = [(a.id, f"{a.name} ({a.account_type})") for a in user_accounts]
    
    user_categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.is_system == True)
    ).all()
    form.category_id.choices = [(c.id, c.name) for c in user_categories]
    
    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            account_id=form.account_id.data,
            category_id=form.category_id.data,
            transaction_type=form.transaction_type.data,
            amount=form.amount.data,
            description=form.description.data,
            transaction_date=form.transaction_date.data,
            payment_method=form.payment_method.data,
            notes=form.notes.data,
            tags=form.tags.data
        )
        db.session.add(transaction)
        db.session.commit()
        
        # Check budget limits and send notifications if exceeded
        if form.transaction_type.data == 'expense' and form.category_id.data:
            from utils import check_budget_limits_and_notify
            try:
                notifications_sent = check_budget_limits_and_notify(
                    current_user.id,
                    form.amount.data,
                    form.category_id.data
                )
                if notifications_sent:
                    flash(f'Transaction added. Budget alert emails sent for: {", ".join(notifications_sent)}', 'warning')
                else:
                    flash('Transaction added successfully!', 'success')
            except Exception as e:
                flash('Transaction added successfully!', 'success')
        else:
            flash('Transaction added successfully!', 'success')
        
        return redirect(url_for('transactions'))
    
    # Set default date to today
    if not form.transaction_date.data:
        form.transaction_date.data = date.today()
    
    return render_template('forms/transaction_form.html', form=form, title='Add Transaction')

@app.route('/transactions/<int:transaction_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_transaction(transaction_id):
    """Edit transaction"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    form = TransactionForm(obj=transaction)
    
    # Populate choices
    user_accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    form.account_id.choices = [(a.id, f"{a.name} ({a.account_type})") for a in user_accounts]
    
    user_categories = Category.query.filter(
        (Category.user_id == current_user.id) | (Category.is_system == True)
    ).all()
    form.category_id.choices = [(c.id, c.name) for c in user_categories]
    
    if form.validate_on_submit():
        transaction.account_id = form.account_id.data
        transaction.category_id = form.category_id.data
        transaction.transaction_type = form.transaction_type.data
        transaction.amount = form.amount.data
        transaction.description = form.description.data
        transaction.transaction_date = form.transaction_date.data
        transaction.payment_method = form.payment_method.data
        transaction.notes = form.notes.data
        transaction.tags = form.tags.data
        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions'))
    
    return render_template('forms/transaction_form.html', form=form, title='Edit Transaction')

@app.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@require_login
def delete_transaction(transaction_id):
    """Delete transaction"""
    transaction = Transaction.query.filter_by(id=transaction_id, user_id=current_user.id).first_or_404()
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/budgets')
@require_login
def budgets():
    """Budget management page"""
    user_budgets = Budget.query.filter_by(user_id=current_user.id, is_active=True).all()
    budget_progress = get_budget_progress(current_user.id)
    
    return render_template('budgets.html', 
                         budgets=user_budgets,
                         budget_progress=budget_progress)

@app.route('/budgets/add', methods=['GET', 'POST'])
@require_login
def add_budget():
    """Add new budget"""
    form = BudgetForm()
    
    # Get expense categories only
    expense_categories = Category.query.filter(
        ((Category.user_id == current_user.id) | (Category.is_system == True)) &
        (Category.type == 'expense')
    ).all()
    form.category_id.choices = [(c.id, c.name) for c in expense_categories]
    
    if form.validate_on_submit():
        budget = Budget(
            user_id=current_user.id,
            category_id=form.category_id.data,
            amount=form.amount.data,
            period=form.period.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(budget)
        db.session.commit()
        flash('Budget created successfully!', 'success')
        return redirect(url_for('budgets'))
    
    # Set default start date to beginning of current month
    if not form.start_date.data:
        today = date.today()
        form.start_date.data = date(today.year, today.month, 1)
    
    return render_template('forms/budget_form.html', form=form, title='Add Budget')

@app.route('/budgets/<int:budget_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_budget(budget_id):
    """Edit budget"""
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    form = BudgetForm(obj=budget)
    
    expense_categories = Category.query.filter(
        ((Category.user_id == current_user.id) | (Category.is_system == True)) &
        (Category.type == 'expense')
    ).all()
    form.category_id.choices = [(c.id, c.name) for c in expense_categories]
    
    if form.validate_on_submit():
        budget.category_id = form.category_id.data
        budget.amount = form.amount.data
        budget.period = form.period.data
        budget.start_date = form.start_date.data
        budget.end_date = form.end_date.data
        db.session.commit()
        flash('Budget updated successfully!', 'success')
        return redirect(url_for('budgets'))
    
    return render_template('forms/budget_form.html', form=form, title='Edit Budget')

@app.route('/budgets/<int:budget_id>/delete', methods=['POST'])
@require_login
def delete_budget(budget_id):
    """Delete budget"""
    budget = Budget.query.filter_by(id=budget_id, user_id=current_user.id).first_or_404()
    budget.is_active = False
    db.session.commit()
    flash('Budget deactivated successfully!', 'success')
    return redirect(url_for('budgets'))

@app.route('/goals')
@require_login
def goals():
    """Savings goals page"""
    user_goals = get_savings_goals_progress(current_user.id)
    return render_template('goals.html', goals=user_goals)

@app.route('/goals/add', methods=['GET', 'POST'])
@require_login
def add_goal():
    """Add new savings goal"""
    form = SavingsGoalForm()
    
    if form.validate_on_submit():
        goal = SavingsGoal(
            user_id=current_user.id,
            name=form.name.data,
            target_amount=form.target_amount.data,
            target_date=form.target_date.data,
            description=form.description.data
        )
        db.session.add(goal)
        db.session.commit()
        flash('Savings goal created successfully!', 'success')
        return redirect(url_for('goals'))
    
    return render_template('forms/goal_form.html', form=form, title='Add Savings Goal')

@app.route('/goals/<int:goal_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_goal(goal_id):
    """Edit savings goal"""
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    form = SavingsGoalForm(obj=goal)
    
    if form.validate_on_submit():
        goal.name = form.name.data
        goal.target_amount = form.target_amount.data
        goal.target_date = form.target_date.data
        goal.description = form.description.data
        db.session.commit()
        flash('Savings goal updated successfully!', 'success')
        return redirect(url_for('goals'))
    
    return render_template('forms/goal_form.html', form=form, title='Edit Savings Goal')

@app.route('/goals/<int:goal_id>/delete', methods=['POST'])
@require_login
def delete_goal(goal_id):
    """Delete savings goal"""
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    db.session.delete(goal)
    db.session.commit()
    flash('Savings goal deleted successfully!', 'success')
    return redirect(url_for('goals'))

@app.route('/reports')
@require_login
def reports():
    """Financial reports page"""
    # Get monthly income/expense trend
    monthly_trend = get_monthly_income_expense_trend(current_user.id)
    
    # Get spending by category for current month
    monthly_spending = get_monthly_spending_by_category(current_user.id)
    
    # Get net worth data
    net_worth_data = calculate_net_worth(current_user.id)
    
    return render_template('reports.html',
                         monthly_trend=monthly_trend,
                         monthly_spending=monthly_spending,
                         net_worth_data=net_worth_data)

@app.route('/profile')
@require_login
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

# API endpoints for charts
@app.route('/api/spending-chart')
@require_login
def spending_chart_data():
    """API endpoint for spending chart data"""
    monthly_spending = get_monthly_spending_by_category(current_user.id)
    
    labels = [item[0] for item in monthly_spending]
    data = [float(item[2]) for item in monthly_spending]
    colors = [item[1] for item in monthly_spending]
    
    return jsonify({
        'labels': labels,
        'data': data,
        'backgroundColor': colors
    })

@app.route('/api/income-expense-trend')
@require_login
def income_expense_trend_data():
    """API endpoint for income vs expense trend"""
    trend_data = get_monthly_income_expense_trend(current_user.id)
    
    months = sorted(trend_data.keys())
    income_data = [trend_data[month]['income'] for month in months]
    expense_data = [trend_data[month]['expense'] for month in months]
    
    return jsonify({
        'labels': months,
        'income': income_data,
        'expense': expense_data
    })

# Voice Assistant Routes
@app.route('/voice-transaction', methods=['POST'])
@require_login
def voice_transaction():
    """Process voice input for transaction"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file provided'})
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'message': 'No audio file selected'})
        
        # Import voice assistant functions
        from voice_assistant import transcribe_audio, process_voice_transaction
        
        # Transcribe the audio
        transcription_result = transcribe_audio(audio_file)
        
        if not transcription_result['success']:
            return jsonify(transcription_result)
        
        transcript = transcription_result['transcript']
        
        # Process the transcript to extract transaction details
        result = process_voice_transaction(current_user.id, transcript)
        
        # Add transcript to response for debugging
        result['transcript'] = transcript
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing voice input: {str(e)}'
        })

@app.route('/voice-suggestions')
@require_login
def voice_suggestions():
    """Get voice command suggestions"""
    from voice_assistant import get_voice_assistant_suggestions
    return jsonify({
        'suggestions': get_voice_assistant_suggestions()
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
