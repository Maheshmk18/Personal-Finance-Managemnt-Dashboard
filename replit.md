# Personal Finance Management System

## Overview

A comprehensive personal finance management web application built with Flask that helps users track income, expenses, budgets, savings goals, and provides financial insights through data visualization. The system supports multiple account types, transaction management, budget tracking, and financial reporting with a modern dark-themed interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme for responsive UI
- **JavaScript Framework**: Vanilla JavaScript with Chart.js for data visualization
- **Styling**: Custom CSS with Bootstrap integration, dark theme optimized
- **User Interface**: Card-based dashboard layout with responsive navigation

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Authentication**: Flask-Login with Replit OAuth integration via Flask-Dance
- **Form Handling**: WTForms with CSRF protection for secure form processing
- **Data Models**: SQLAlchemy models with relationships for users, accounts, transactions, budgets, categories, and goals
- **Session Management**: Flask sessions with permanent session configuration

### Database Design
- **ORM**: SQLAlchemy with DeclarativeBase for model definitions
- **Models**: User, OAuth, Account, Transaction, Category, Budget, SavingsGoal, Bill
- **Relationships**: One-to-many relationships between users and their financial data
- **Data Types**: Decimal precision for financial amounts, datetime tracking for audit trails

### Application Structure
- **Modular Design**: Separate files for models, forms, routes, utilities, and authentication
- **Template Organization**: Base template with inheritance, form templates, and specialized views
- **Static Assets**: Organized CSS and JavaScript files for styling and interactivity

## External Dependencies

### Authentication Services
- **Replit Auth**: OAuth integration for user authentication and authorization
- **Flask-Dance**: OAuth consumer for handling authentication flows

### Database
- **PostgreSQL**: Primary database (configurable via DATABASE_URL environment variable)
- **SQLAlchemy**: Database connection pooling with health checks and connection recycling

### Frontend Libraries
- **Bootstrap 5**: UI component framework with dark theme
- **Font Awesome**: Icon library for consistent iconography
- **Chart.js**: Data visualization library for financial charts and graphs

### Python Packages
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-Login**: User session management
- **PyJWT**: JSON Web Token handling for authentication
- **Werkzeug**: WSGI utilities and proxy handling