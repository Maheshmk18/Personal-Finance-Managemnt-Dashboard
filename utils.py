from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, extract
from models import Transaction, Budget, Account, Category, SavingsGoal, Bill, User
from app import db
import calendar

def get_account_balance(account_id):
    """Calculate the current balance of an account based on transactions"""
    income = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.account_id == account_id,
            Transaction.transaction_type == 'income'
        )
    ).scalar() or Decimal('0')
    
    expenses = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.account_id == account_id,
            Transaction.transaction_type == 'expense'
        )
    ).scalar() or Decimal('0')
    
    return income - expenses

def get_monthly_spending_by_category(user_id, month=None, year=None):
    """Get spending breakdown by category for a given month"""
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
    
    query = db.session.query(
        Category.name,
        Category.color,
        func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'expense',
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        )
    ).group_by(Category.id, Category.name, Category.color)
    
    return query.all()

def get_budget_progress(user_id, month=None, year=None):
    """Get budget progress for the current or specified month"""
    if not month:
        month = datetime.now().month
    if not year:
        year = datetime.now().year
    
    # Get all active budgets for the user
    budgets = Budget.query.filter(
        and_(
            Budget.user_id == user_id,
            Budget.is_active == True
        )
    ).all()
    
    budget_progress = []
    for budget in budgets:
        # Calculate spent amount for this category in the current month
        spent = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.category_id == budget.category_id,
                Transaction.transaction_type == 'expense',
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            )
        ).scalar() or Decimal('0')
        
        progress_percent = float((spent / budget.amount) * 100) if budget.amount > 0 else 0
        
        budget_progress.append({
            'budget': budget,
            'spent': spent,
            'remaining': budget.amount - spent,
            'progress_percent': progress_percent,
            'is_over_budget': spent > budget.amount
        })
    
    return budget_progress

def get_recent_transactions(user_id, limit=10):
    """Get recent transactions for a user"""
    return Transaction.query.filter(Transaction.user_id == user_id)\
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())\
        .limit(limit).all()

def get_monthly_income_expense_trend(user_id, months=12):
    """Get monthly income vs expense trend for the last N months"""
    end_date = date.today()
    start_date = end_date - timedelta(days=30 * months)
    
    # Get monthly aggregates
    query = db.session.query(
        extract('year', Transaction.transaction_date).label('year'),
        extract('month', Transaction.transaction_date).label('month'),
        Transaction.transaction_type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_type.in_(['income', 'expense'])
        )
    ).group_by('year', 'month', Transaction.transaction_type)\
    .order_by('year', 'month')
    
    results = query.all()
    
    # Organize data by month
    monthly_data = {}
    for result in results:
        month_key = f"{int(result.year)}-{int(result.month):02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        monthly_data[month_key][result.transaction_type] = float(result.total)
    
    return monthly_data

def get_savings_goals_progress(user_id):
    """Get savings goals with progress calculation"""
    goals = SavingsGoal.query.filter(SavingsGoal.user_id == user_id).all()
    
    goals_with_progress = []
    for goal in goals:
        progress_percent = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
        
        days_remaining = None
        if goal.target_date:
            days_remaining = (goal.target_date - date.today()).days
        
        goals_with_progress.append({
            'goal': goal,
            'progress_percent': progress_percent,
            'days_remaining': days_remaining,
            'remaining_amount': goal.target_amount - goal.current_amount
        })
    
    return goals_with_progress

def get_upcoming_bills(user_id, days_ahead=30):
    """Get bills due in the next N days"""
    end_date = date.today() + timedelta(days=days_ahead)
    
    return Bill.query.filter(
        and_(
            Bill.user_id == user_id,
            Bill.due_date <= end_date,
            Bill.is_paid == False
        )
    ).order_by(Bill.due_date).all()

def calculate_net_worth(user_id):
    """Calculate user's net worth based on all accounts"""
    accounts = Account.query.filter(
        and_(
            Account.user_id == user_id,
            Account.is_active == True
        )
    ).all()
    
    assets = Decimal('0')
    liabilities = Decimal('0')
    
    for account in accounts:
        balance = get_account_balance(account.id)
        if account.account_type in ['checking', 'savings', 'investment']:
            assets += balance
        elif account.account_type == 'credit':
            liabilities += abs(balance)  # Credit card balances are typically negative
    
    return {
        'assets': assets,
        'liabilities': liabilities,
        'net_worth': assets - liabilities
    }

def format_currency(amount, currency='USD'):
    """Format amount as currency"""
    if currency == 'USD':
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def get_financial_health_score(user_id):
    """Calculate a simple financial health score based on various factors"""
    score = 0
    max_score = 100
    
    # Factor 1: Budget adherence (40 points)
    budget_progress = get_budget_progress(user_id)
    if budget_progress:
        over_budget_count = sum(1 for bp in budget_progress if bp['is_over_budget'])
        budget_score = max(0, 40 - (over_budget_count * 10))
        score += budget_score
    
    # Factor 2: Savings goals progress (30 points)
    goals_progress = get_savings_goals_progress(user_id)
    if goals_progress:
        avg_progress = sum(gp['progress_percent'] for gp in goals_progress) / len(goals_progress)
        savings_score = min(30, avg_progress * 0.3)
        score += savings_score
    
    # Factor 3: Net worth positivity (30 points)
    net_worth_data = calculate_net_worth(user_id)
    if net_worth_data['net_worth'] > 0:
        score += 30
    elif net_worth_data['net_worth'] > -1000:  # Small negative is ok
        score += 15
    
    return min(max_score, score)

def check_budget_limits_and_notify(user_id, new_transaction_amount=None, category_id=None):
    """Check if any budget limits are exceeded and send email notifications"""
    from email_service import send_budget_alert_email
    
    # Get current budget progress
    budget_progress = get_budget_progress(user_id)
    
    # If a new transaction was just added, update the relevant budget progress
    if new_transaction_amount and category_id:
        for bp in budget_progress:
            if bp['budget'].category_id == category_id:
                bp['spent'] += new_transaction_amount
                bp['progress_percent'] = float((bp['spent'] / bp['budget'].amount) * 100)
                bp['is_over_budget'] = bp['spent'] > bp['budget'].amount
                break
    
    # Check for budget overages and send notifications
    user = User.query.get(user_id)
    if not user or not user.email:
        return
    
    notifications_sent = []
    for bp in budget_progress:
        if bp['is_over_budget']:
            # Check if we've already sent a notification for this budget this month
            # In a real app, you'd store notification history in the database
            budget_info = {
                'category_name': bp['budget'].category.name,
                'period': bp['budget'].period,
                'start_date': bp['budget'].start_date
            }
            
            try:
                success = send_budget_alert_email(
                    user.email,
                    budget_info,
                    float(bp['spent']),
                    float(bp['budget'].amount)
                )
                
                if success:
                    notifications_sent.append(budget_info['category_name'])
                    
            except Exception as e:
                print(f"Error sending budget notification: {str(e)}")
    
    return notifications_sent

def get_budget_overage_summary(user_id):
    """Get summary of budget overages for the current month"""
    budget_progress = get_budget_progress(user_id)
    
    overages = []
    total_overage = Decimal('0')
    
    for bp in budget_progress:
        if bp['is_over_budget']:
            overage_amount = bp['spent'] - bp['budget'].amount
            overages.append({
                'category': bp['budget'].category.name,
                'budget_amount': bp['budget'].amount,
                'spent_amount': bp['spent'],
                'overage_amount': overage_amount,
                'overage_percent': float((overage_amount / bp['budget'].amount) * 100)
            })
            total_overage += overage_amount
    
    return {
        'overages': overages,
        'total_overage': total_overage,
        'categories_over_budget': len(overages)
    }
