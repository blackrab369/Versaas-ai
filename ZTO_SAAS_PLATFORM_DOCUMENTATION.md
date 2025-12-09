# Virsaas Virtual Software Inc. - SaaS Platform Documentation

## Overview

This document provides comprehensive information about the Virsaas Virtual Software Inc. SaaS platform - a complete business solution that transforms the original virtual company simulation into a production-ready SaaS application with user accounts, subscriptions, persistent simulations, and real document outputs.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Features](#features)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [API Documentation](#api-documentation)
7. [Database Schema](#database-schema)
8. [Security](#security)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

## System Architecture

### Technology Stack

**Backend Framework:**

- Flask 2.3+ - Web framework
- Flask-SQLAlchemy 3.0+ - Database ORM
- Flask-Login 0.6+ - User authentication

**Database:**

- SQLite (development) / PostgreSQL (production)
- SQLAlchemy 2.0+ - Database toolkit

**Frontend:**

- HTML5/CSS3 with Tailwind CSS
- JavaScript (ES6+)
- Plotly.js - Interactive charts
- Font Awesome - Icons

**Core Components:**

- Pygame-ce 2.3+ - 2.5D simulation engine
- Plotly 5.15+ - Financial dashboard
- Pandas 2.0+ - Data processing
- NumPy 1.24+ - Numerical computing

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Flask)                     │
├─────────────────────────────────────────────────────────────┤
│  Authentication  │  Project Management │  Simulation Engine  │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                      │
├─────────────────────────────────────────────────────────────┤
│  User Accounts  │  Subscriptions  │  Document Generation   │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                         │
├─────────────────────────────────────────────────────────────┤
│  SQLite/PostgreSQL  │  File System  │  Memory Cache       │
└─────────────────────────────────────────────────────────────┘
```

## Features

### Core Features

1. **User Account System**

   - Registration and login
   - Password hashing and security
   - Session management
   - User roles and permissions

2. **Subscription Management**

   - Free 1-hour trial
   - Monthly premium subscription ($49/month)
   - Enterprise custom plans
   - Subscription status tracking

3. **Project Management**

   - Multiple projects per user
   - Project creation and deletion
   - Project status tracking
   - Persistent simulation state

4. **Virtual Company Simulation**

   - 25 autonomous AI employees
   - 2.5D isometric office visualization
   - Real-time agent movement and interaction
   - Persistent simulation (24/7 operation)

5. **CEO Chat Interface**

   - Natural language communication
   - Real-time message handling
   - AI-powered responses
   - Message history

6. **Financial Dashboard**

   - Real-time financial metrics
   - Interactive charts and graphs
   - Revenue tracking
   - Progress indicators

7. **Document Generation**

   - Business plan generation
   - Legal document templates
   - Financial projections
   - Technical documentation

8. **Project Export**
   - ZIP file generation
   - Complete project package
   - Source code and documentation
   - Business assets

### Advanced Features

1. **Persistent Simulation**

   - Continues running when user closes browser
   - Independent project simulations
   - State saving and restoration
   - Automatic progress tracking

2. **Multi-Tenant Architecture**

   - User isolation
   - Resource management
   - Scalable design
   - Performance optimization

3. **Security Features**

   - SHA-256 audit trails
   - Encrypted passwords
   - Session security
   - Data protection

4. **Business Intelligence**
   - Usage analytics
   - Performance metrics
   - User behavior tracking
   - Revenue optimization

## Installation

### Prerequisites

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 1GB disk space
- Internet connection for dependencies

### Step-by-Step Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd zto-saas-platform
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements_saas.txt
   ```

4. **Initialize Database**

   ```bash
   python -c "from zto_saas_platform import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Create Required Directories**

   ```bash
   mkdir -p user_projects
   mkdir -p instance
   ```

6. **Run the Application**
   ```bash
   python zto_saas_platform.py
   ```

### Development Installation

For development with debug mode enabled:

```bash
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows
python zto_saas_platform.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database Configuration
DATABASE_URL=sqlite:///zto_saas.db
# For production: DATABASE_URL=postgresql://user:pass@localhost/zto_db

# Stripe Configuration (for production)
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Security Configuration
SECURITY_PASSWORD_SALT=your-password-salt

# Application Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=user_projects

# Simulation Configuration
SIMULATION_SPEED=1.0
SIMULATION_SAVE_INTERVAL=3600  # Save every hour
```

### Configuration Files

**config.py**

```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///zto_saas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))

    # Security
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'dev-salt'

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    # Stripe configuration
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

    # Application configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'user_projects'
    SIMULATION_SPEED = float(os.environ.get('SIMULATION_SPEED', 1.0))
    SIMULATION_SAVE_INTERVAL = int(os.environ.get('SIMULATION_SAVE_INTERVAL', 3600))

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

## Usage

### Getting Started

1. **Access the Web Interface**

   - Open your browser and navigate to `http://localhost:5000`
   - You'll see the main landing page with feature descriptions

2. **Create an Account**

   - Click "Register" or go to `/register`
   - Fill in the registration form
   - You'll receive a 1-hour free trial

3. **Create Your First Project**

   - After registration, you'll be redirected to the dashboard
   - Click "Create New Project"
   - Fill in project details and submit

4. **Monitor Your Virtual Company**
   - Click on your project to enter the project view
   - Watch the 2.5D office simulation
   - Chat with your AI CEO
   - Monitor financial progress

### User Interface

**Main Pages:**

- **Index Page** (`/`) - Landing page with features and pricing
- **Register** (`/register`) - User registration form
- **Login** (`/login`) - User authentication
- **Dashboard** (`/dashboard`) - Project management interface
- **Project View** (`/project/<id>`) - Detailed project simulation
- **Subscription** (`/subscribe`) - Plan selection and payment

**Project Interface:**

- **Virtual Office** - 2.5D simulation with agent movement
- **CEO Chat** - Real-time communication interface
- **Financial Dashboard** - Interactive charts and metrics
- **Team Status** - Live agent activity monitoring
- **Quick Actions** - Document generation and export

### Creating Projects

1. **From Dashboard**

   - Click "Create New Project" button
   - Fill in project name and description
   - Submit to start simulation

2. **Project Details**

   - Name: Your project/product name
   - Description: Detailed idea description
   - Business goals and target market

3. **Simulation Starts Automatically**
   - 25 AI employees begin work
   - Virtual office becomes active
   - Progress tracking begins

### Interacting with Your Virtual Company

**CEO Chat:**

- Type messages in the chat input
- Ask about project status
- Provide business direction
- Request specific features

**Monitoring Progress:**

- Watch agent movements in virtual office
- Check financial dashboard for metrics
- Review team status for current activities
- Monitor recent activity feed

**Document Generation:**

- Click "Generate Documents" button
- System creates business plan, legal docs
- Documents saved to project output folder
- Available for download as ZIP

### Subscription Management

**Free Trial:**

- 1-hour full access to all features
- Limited to 1 project
- No credit card required

**Premium Subscription:**

- $49/month unlimited access
- Unlimited projects
- Priority support
- Advanced features

**Enterprise:**

- Custom pricing
- White-label solutions
- Private deployment
- Custom integrations

## API Documentation

### Authentication Endpoints

**POST /register**

```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**POST /login**

```json
{
  "username": "string",
  "password": "string"
}
```

### Project Endpoints

**POST /create_project**

```json
{
  "name": "string",
  "description": "string"
}
```

**GET /api/project/<project_id>/status**
Returns current project status and simulation data.

**POST /api/project/<project_id>/message**

```json
{
  "message": "string"
}
```

**POST /api/project/<project_id>/generate_documents**
Generates business documents for the project.

**GET /api/project/<project_id>/download**
Downloads project as ZIP file.

### Subscription Endpoints

**POST /api/create_checkout_session**
Creates Stripe checkout session for subscription.

## Database Schema

### User Table

```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    subscription_type VARCHAR(20) DEFAULT 'free',
    subscription_status VARCHAR(20) DEFAULT 'active',
    subscription_id VARCHAR(100),
    trial_end_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

### Project Table

```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id VARCHAR(36) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    simulation_data TEXT,
    revenue FLOAT DEFAULT 0.0,
    cash_burn FLOAT DEFAULT 0.0,
    days_elapsed INTEGER DEFAULT 0,
    current_phase VARCHAR(50) DEFAULT 'Phase 0 - Idea Intake',
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

### Document Table

```sql
CREATE TABLE document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    content_hash VARCHAR(64),
    FOREIGN KEY (project_id) REFERENCES project (id)
);
```

### Payment Table

```sql
CREATE TABLE payment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    stripe_payment_id VARCHAR(100) UNIQUE NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR(3) DEFAULT 'usd',
    status VARCHAR(20) DEFAULT 'pending',
    payment_type VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project (id)
);
```

## Security

### Authentication

- Password hashing using Werkzeug's security utilities
- Session-based authentication with Flask-Login
- CSRF protection on all forms
- Secure session cookies

### Authorization

- User role-based access control
- Project ownership verification
- Subscription-based feature access
- API endpoint protection

### Data Protection

- Password hashing with salt
- Encrypted sensitive data
- Secure file uploads
- Input validation and sanitization

### Audit Trail

- SHA-256 hashing of all actions
- Complete activity logging
- User action tracking
- System event monitoring

## Deployment

### Development Deployment

```bash
# Set environment variables
export FLASK_ENV=development
export SECRET_KEY=your-dev-secret

# Run the application
python zto_saas_platform.py
```

### Production Deployment

**Using Gunicorn:**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 zto_saas_platform:app
```

**Using uWSGI:**

```bash
pip install uwsgi
uwsgi --http :5000 --wsgi-file zto_saas_platform.py --callable app
```

**Using Docker:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements_saas.txt .
RUN pip install -r requirements_saas.txt

COPY . .

EXPOSE 5000

CMD ["python", "zto_saas_platform.py"]
```

### Environment-Specific Deployment

**Development:**

```bash
export FLASK_ENV=development
export DEBUG=True
python zto_saas_platform.py
```

**Staging:**

```bash
export FLASK_ENV=production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@staging/db
python zto_saas_platform.py
```

**Production:**

```bash
export FLASK_ENV=production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@production/db
export SECRET_KEY=your-production-secret
python zto_saas_platform.py
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**

   ```bash
   # Check database file permissions
   ls -la zto_saas.db

   # Recreate database
   rm zto_saas.db
   python -c "from zto_saas_platform import app, db; app.app_context().push(); db.create_all()"
   ```

2. **Import Error**

   ```bash
   # Check Python path
   echo $PYTHONPATH

   # Install missing dependencies
   pip install -r requirements_saas.txt
   ```

3. **Port Already in Use**

   ```bash
   # Find process using port 5000
   lsof -i :5000

   # Kill the process
   kill -9 <pid>
   ```

4. **Simulation Not Starting**

   ```bash
   # Check project directory permissions
   ls -la user_projects/

   # Create missing directories
   mkdir -p user_projects
   ```

5. **Template Not Found**

   ```bash
   # Check templates directory
   ls -la templates/

   # Verify template files exist
   ```

### Performance Optimization

1. **Database Optimization**

   - Use connection pooling
   - Add database indexes
   - Optimize queries

2. **Memory Management**

   - Monitor simulation memory usage
   - Implement resource limits
   - Use efficient data structures

3. **Simulation Performance**
   - Adjust simulation speed
   - Limit concurrent simulations
   - Optimize agent algorithms

### Monitoring and Logging

1. **Application Logs**

   ```bash
   tail -f logs/zto_saas.log
   ```

2. **Database Logs**

   ```bash
   tail -f logs/database.log
   ```

3. **Simulation Logs**
   ```bash
   tail -f logs/simulation.log
   ```

### Support and Maintenance

1. **Regular Backups**

   ```bash
   # Database backup
   sqlite3 zto_saas.db ".backup backup.db"

   # Project files backup
   tar -czf backup.tar.gz user_projects/
   ```

2. **Security Updates**

   - Keep dependencies updated
   - Monitor security advisories
   - Regular security audits

3. **Performance Monitoring**
   - Monitor response times
   - Track resource usage
   - Analyze user behavior

## Conclusion

The Virsaas Virtual Software Inc. SaaS platform represents a complete transformation of the original virtual company simulation into a production-ready business application. With comprehensive user management, persistent simulations, real document generation, and subscription-based access, it provides a complete solution for entrepreneurs looking to leverage AI-powered development teams.

The platform's architecture supports scalability, security, and maintainability while delivering an engaging user experience through the 2.5D virtual office simulation and real-time interaction capabilities.

For additional support, documentation updates, or feature requests, please refer to the project's issue tracker or contact the development team.

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-04  
**Author:** ZTO Virtual Development Team  
**License:** Commercial
