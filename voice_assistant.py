import os
import json
from openai import OpenAI
from datetime import datetime, date
from decimal import Decimal
from flask import current_app
from models import Transaction, Account, Category
from app import db

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def process_voice_transaction(user_id, audio_transcript):
    """Process voice input and extract transaction details using OpenAI"""
    try:
        # Use OpenAI to extract transaction details from voice input
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial assistant that extracts transaction details from voice input.
                    
                    Extract the following information from the user's voice input:
                    - amount: The monetary amount (as a number, no currency symbols)
                    - description: A brief description of the transaction
                    - transaction_type: "expense" or "income"
                    - category: One of these categories based on the description:
                      - Food & Dining (for restaurants, groceries, food delivery)
                      - Transportation (for gas, uber, taxi, parking)
                      - Shopping (for retail purchases, online shopping)
                      - Entertainment (for movies, games, streaming)
                      - Bills & Utilities (for rent, electricity, internet)
                      - Healthcare (for medical, pharmacy, doctor)
                      - Travel (for hotels, flights, vacation)
                      - Education (for school, courses, books)
                      - Personal Care (for haircuts, beauty, gym)
                      - Home & Garden (for home improvement, cleaning)
                      - Salary (for income from work)
                      - Business (for business income)
                      - Investments (for investment returns)
                      - Other (if none of the above fit)
                    
                    Respond with JSON only in this exact format:
                    {
                        "amount": number,
                        "description": "string",
                        "transaction_type": "expense|income",
                        "category": "category_name",
                        "confidence": number_between_0_and_1
                    }
                    
                    If you cannot extract clear transaction information, set confidence to 0.
                    """
                },
                {
                    "role": "user",
                    "content": f"Extract transaction details from: {audio_transcript}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        # Parse the response
        transaction_data = json.loads(response.choices[0].message.content)
        
        # Validate confidence
        if transaction_data.get('confidence', 0) < 0.6:
            return {
                'success': False,
                'message': 'Could not understand the transaction details clearly. Please try again.',
                'confidence': transaction_data.get('confidence', 0)
            }
        
        # Get user's accounts
        user_accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
        if not user_accounts:
            return {
                'success': False,
                'message': 'No active accounts found. Please add an account first.'
            }
        
        # Use the first account (or primary checking account if available)
        account = user_accounts[0]
        for acc in user_accounts:
            if acc.account_type == 'checking':
                account = acc
                break
        
        # Find the category
        category = Category.query.filter(
            ((Category.user_id == user_id) | (Category.is_system == True)) &
            (Category.name.ilike(f"%{transaction_data['category']}%")) &
            (Category.type == transaction_data['transaction_type'])
        ).first()
        
        # If no specific category found, use default
        if not category:
            default_name = 'Other' if transaction_data['transaction_type'] == 'expense' else 'Other Income'
            category = Category.query.filter_by(
                name=default_name,
                is_system=True,
                type=transaction_data['transaction_type']
            ).first()
        
        # Create the transaction
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            category_id=category.id if category else None,
            amount=Decimal(str(transaction_data['amount'])),
            description=transaction_data['description'],
            transaction_date=date.today(),
            transaction_type=transaction_data['transaction_type'],
            payment_method='voice_input',
            notes=f'Added via voice assistant (confidence: {transaction_data["confidence"]:.1%})'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Check budget limits for expenses
        if transaction_data['transaction_type'] == 'expense' and category:
            from utils import check_budget_limits_and_notify
            try:
                notifications_sent = check_budget_limits_and_notify(
                    user_id,
                    Decimal(str(transaction_data['amount'])),
                    category.id
                )
                budget_alert = len(notifications_sent) > 0
            except:
                budget_alert = False
        else:
            budget_alert = False
        
        return {
            'success': True,
            'message': f'Transaction added: {transaction_data["transaction_type"]} of ${transaction_data["amount"]:.2f} for {transaction_data["description"]}',
            'transaction': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'description': transaction.description,
                'type': transaction.transaction_type,
                'category': category.name if category else 'Uncategorized',
                'account': account.name,
                'date': transaction.transaction_date.strftime('%Y-%m-%d')
            },
            'confidence': transaction_data['confidence'],
            'budget_alert': budget_alert
        }
        
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON decode error in voice processing: {str(e)}")
        return {
            'success': False,
            'message': 'Error processing voice input. Please try again.'
        }
    except Exception as e:
        current_app.logger.error(f"Error processing voice transaction: {str(e)}")
        return {
            'success': False,
            'message': f'Error processing transaction: {str(e)}'
        }

def transcribe_audio(audio_file):
    """Transcribe audio file using OpenAI Whisper"""
    try:
        # Use OpenAI Whisper for transcription
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        return {
            'success': True,
            'transcript': transcript.text
        }
    except Exception as e:
        current_app.logger.error(f"Error transcribing audio: {str(e)}")
        return {
            'success': False,
            'message': f'Error transcribing audio: {str(e)}'
        }

def get_voice_assistant_suggestions():
    """Get example voice commands for users"""
    return [
        "I spent $15 on lunch at McDonald's",
        "Paid $50 for gas at Shell station",
        "Received $2500 salary from work",
        "Bought groceries for $120 at Walmart",
        "Paid $35 for Netflix and Spotify subscriptions",
        "Got $25 cash back from return at Target",
        "Spent $8 on coffee at Starbucks",
        "Paid $150 for electric bill",
        "Earned $300 from freelance project",
        "Bought clothes for $80 at the mall"
    ]