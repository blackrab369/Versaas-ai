#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. - SaaS Platform
Complete business platform with user accounts, subscriptions, and persistent simulations
"""

import os
import sys
import json
import sqlite3
import hashlib
import secrets
import time
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from functools import wraps
import logging

# Flask imports
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

# Add project path
sys.path.append(str(Path(__file__).parent / 'ZTO_Projects' / 'ZTO_Demo'))
from zto_kernel import get_orchestrator, ZTOOrchestrator

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zto_saas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ZTO-SaaS')

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    subscription_type = db.Column(db.String(20), default='free')
    subscription_status = db.Column(db.String(20), default='active')
    subscription_id = db.Column(db.String(100))
    trial_end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(36), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    simulation_data = db.Column(db.Text)  # JSON serialized simulation state
    
    # Business metrics
    revenue = db.Column(db.Float, default=0.0)
    cash_burn = db.Column(db.Float, default=0.0)
    days_elapsed = db.Column(db.Integer, default=0)
    current_phase = db.Column(db.String(50), default='Phase 0 - Idea Intake')
    
    # Relationships
    documents = db.relationship('Document', backref='project', lazy=True)
    payments = db.relationship('Payment', backref='project', lazy=True)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # business_plan, legal_docs, financial_docs
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    content_hash = db.Column(db.String(64))

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    stripe_payment_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(20), default='pending')
    payment_type = db.Column(db.String(20), nullable=False)  # subscription, project_premium
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Simulation Manager
class SimulationManager:
    def __init__(self):
        self.active_simulations = {}  # project_id -> orchestrator_instance
        self.simulation_threads = {}  # project_id -> thread
        self.lock = threading.Lock()
    
    def start_simulation(self, project_id, user_id, initial_idea=""):
        """Start a new simulation for a project"""
        with self.lock:
            if project_id in self.active_simulations:
                return self.active_simulations[project_id]
            
            # Create new orchestrator
            orchestrator = ZTOOrchestrator(project_slug=project_id)
            
            # Load saved state if exists
            project = Project.query.filter_by(project_id=project_id).first()
            if project and project.simulation_data:
                try:
                    saved_state = json.loads(project.simulation_data)
                    orchestrator.company_state.update(saved_state)
                except:
                    pass
            
            # Process initial idea if provided
            if initial_idea:
                orchestrator.process_owner_request(initial_idea)
            
            # Start simulation thread
            def simulation_loop():
                while project_id in self.active_simulations:
                    try:
                        orchestrator.run_simulation_step()
                        
                        # Save state every hour (simulated)
                        if int(orchestrator.company_state['days_elapsed'] * 24) % 60 == 0:
                            self.save_simulation_state(project_id, orchestrator)
                        
                        time.sleep(1)  # 1 second = 1 hour in simulation
                    except Exception as e:
                        logger.error(f"Simulation error for {project_id}: {e}")
                        break
            
            thread = threading.Thread(target=simulation_loop, daemon=True)
            thread.start()
            
            self.active_simulations[project_id] = orchestrator
            self.simulation_threads[project_id] = thread
            
            return orchestrator
    
    def stop_simulation(self, project_id):
        """Stop a simulation"""
        with self.lock:
            if project_id in self.active_simulations:
                orchestrator = self.active_simulations[project_id]
                self.save_simulation_state(project_id, orchestrator)
                del self.active_simulations[project_id]
                del self.simulation_threads[project_id]
    
    def get_simulation(self, project_id):
        """Get active simulation or start new one"""
        with self.lock:
            if project_id in self.active_simulations:
                return self.active_simulations[project_id]
            else:
                # Try to load from database
                project = Project.query.filter_by(project_id=project_id).first()
                if project:
                    return self.start_simulation(project_id, project.user_id)
                return None
    
    def save_simulation_state(self, project_id, orchestrator):
        """Save simulation state to database"""
        project = Project.query.filter_by(project_id=project_id).first()
        if project:
            project.simulation_data = json.dumps(orchestrator.company_state)
            project.last_active = datetime.utcnow()
            project.revenue = orchestrator.company_state['revenue']
            project.cash_burn = orchestrator.company_state['cash_burn']
            project.days_elapsed = orchestrator.company_state['days_elapsed']
            project.current_phase = orchestrator.company_state['phase']
            db.session.commit()

# Global simulation manager
sim_manager = SimulationManager()

# Utility functions
def generate_project_id():
    """Generate unique project ID"""
    return str(uuid.uuid4())

def create_project_directory(project_id):
    """Create project directory structure"""
    base_path = Path(f"user_projects/{project_id}")
    directories = [
        base_path / ".docs",
        base_path / ".design", 
        base_path / ".src",
        base_path / ".qa",
        base_path / ".finance",
        base_path / ".legal",
        base_path / "output"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    return base_path

def generate_business_plan(project):
    """Generate comprehensive business plan"""
    orchestrator = sim_manager.get_simulation(project.project_id)
    if not orchestrator:
        return None
    
    business_plan = f"""# Business Plan: {project.name}

## Executive Summary
**Company Name**: Virsaas Virtual Software Inc.
**Project**: {project.name}
**Date**: {datetime.now().strftime('%B %d, %Y')}
**Status**: {project.current_phase}

### Mission Statement
{project.description}

### Financial Projections
- **Current Revenue**: ${project.revenue:,.2f}
- **Cash Burn Rate**: ${2500:.2f}/day
- **Days Elapsed**: {project.days_elapsed}
- **Runway Remaining**: {max(0, (180 - project.days_elapsed))} days
- **Target**: $1,000,000 revenue by day 180

## Market Analysis
### Target Market
- Primary: [User-defined target market]
- Secondary: [Market segments]

### Competitive Landscape
- Direct competitors analysis
- Indirect competitors analysis
- Competitive advantages

## Product Strategy
### Core Features
- Feature 1: [Detailed description]
- Feature 2: [Detailed description]
- Feature 3: [Detailed description]

### Technology Stack
- Frontend: React/Next.js
- Backend: Node.js/Python
- Database: PostgreSQL
- Infrastructure: Azure/AWS

## Business Model
### Revenue Streams
1. **Primary Revenue**: [Description]
2. **Secondary Revenue**: [Description]
3. **Subscription Model**: [Description]

### Pricing Strategy
- Tier 1: $X/month
- Tier 2: $Y/month  
- Tier 3: $Z/month

## Financial Plan
### Startup Costs
- Development: $50,000
- Infrastructure: $5,000
- Legal & Compliance: $10,000
- Marketing: $20,000
- **Total**: $85,000

### Revenue Projections
- Month 1-3: $0 (Development)
- Month 4-6: $10,000 (Beta testing)
- Month 7-12: $50,000/month
- Year 2: $100,000/month
- **Year 1 Total**: $300,000
- **Year 2 Total**: $1,200,000

## Team Structure
### Core Team (Virtual AI Agents)
- **Development Team**: 10 specialized engineers
- **Design Team**: 2 UX/UI experts
- **Management Team**: 4 project/business managers
- **Administration**: 4 legal/finance/support staff

### Advisory Board
- Industry experts
- Technical advisors
- Legal counsel
- Financial advisors

## Risk Assessment
### Technical Risks
- **Risk**: Technology stack complexity
- **Mitigation**: Proven technologies, experienced team

### Market Risks  
- **Risk**: Competitive pressure
- **Mitigation**: Unique value proposition, rapid iteration

### Financial Risks
- **Risk**: Cash flow management
- **Mitigation**: Lean operations, milestone-based funding

## Implementation Timeline
### Phase 1: Discovery (Days 1-5)
- Market research
- User interviews
- Technical architecture

### Phase 2: MVP Development (Days 6-20)
- Core feature development
- Testing and validation
- Infrastructure setup

### Phase 3: Beta Launch (Days 21-30)
- Private beta testing
- User feedback integration
- Performance optimization

### Phase 4: Public Launch (Days 31-44)
- Marketing campaign
- Public release
- Customer acquisition

### Phase 5: Scale (Days 45-180)
- Feature expansion
- Market growth
- Revenue optimization

## Success Metrics
### Key Performance Indicators
- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV)
- Churn Rate
- Net Promoter Score (NPS)

### Milestones
- Day 30: MVP launch
- Day 60: $10,000 MRR
- Day 90: $50,000 MRR  
- Day 180: $1,000,000 ARR

---
*This business plan was generated by Virsaas Virtual Software Inc. AI agents*
*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    return business_plan

def generate_legal_documents(project):
    """Generate legal document templates"""
    legal_docs = {}
    
    # Terms of Service
    legal_docs['terms_of_service.md'] = f"""# Terms of Service
    
**Effective Date**: {datetime.now().strftime('%B %d, %Y')}
**Company**: Virsaas Virtual Software Inc.
**Product**: {project.name}

## 1. Acceptance of Terms
By accessing and using {project.name}, you agree to be bound by these Terms of Service.

## 2. Description of Service
{project.name} provides [describe service functionality].

## 3. User Obligations
- Users must provide accurate information
- Users are responsible for maintaining account security
- Users must comply with all applicable laws

## 4. Intellectual Property
All content, features, and functionality are owned by Virsaas Virtual Software Inc.

## 5. Limitation of Liability
The service is provided "as is" without warranties of any kind.

## 6. Termination
We reserve the right to terminate accounts for violation of these terms.

## 7. Changes to Terms
We may modify these terms at any time. Continued use constitutes acceptance.

## 8. Contact Information
For questions about these terms, contact: legal@zto-inc.com
"""
    
    # Privacy Policy
    legal_docs['privacy_policy.md'] = f"""# Privacy Policy

**Effective Date**: {datetime.now().strftime('%B %d, %Y')}

## 1. Information We Collect
- **Personal Information**: Name, email, payment information
- **Usage Data**: How you interact with our service
- **Technical Data**: Device information, log data

## 2. How We Use Information
- To provide and maintain our service
- To process payments and subscriptions
- To improve user experience
- To communicate with users

## 3. Data Protection
- Industry-standard encryption
- Regular security audits
- Limited access to personal data

## 4. Third-Party Services
We may use third-party services for payment processing and analytics.

## 5. User Rights
- Access your personal data
- Correct inaccurate data
- Request deletion of data
- Opt-out of marketing communications

## 6. Data Retention
We retain data only as long as necessary to provide our services.

## 7. Contact Information
For privacy questions, contact: privacy@zto-inc.com
"""
    
    # Customer Agreement
    legal_docs['customer_agreement.md'] = f"""# Customer Agreement

**Agreement Date**: {datetime.now().strftime('%B %d, %Y')}

This Customer Agreement ("Agreement") is entered into by and between:

**Virsaas Virtual Software Inc.** ("Company")
and
**Customer** ("You" or "Customer")

## 1. Service Description
Company agrees to provide {project.name} services as described in the product documentation.

## 2. Payment Terms
- Subscription fees are billed monthly in advance
- All payments are non-refundable
- Late payments may result in service suspension

## 3. Service Level Agreement
- 99.9% uptime guarantee
- 24-hour response time for support issues
- Regular security updates and maintenance

## 4. Intellectual Property
- Customer retains ownership of their data
- Company retains ownership of the platform and software
- Customer grants Company right to use data for service provision

## 5. Confidentiality
Both parties agree to maintain confidentiality of proprietary information.

## 6. Limitation of Liability
Company's total liability shall not exceed the amount paid by Customer in the 12 months prior.

## 7. Termination
Either party may terminate with 30 days written notice.

## 8. Governing Law
This agreement shall be governed by the laws of Delaware.

---
*This legal document template was generated by ZTO Inc. AI agents*
"""
    
    return legal_docs

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            trial_end_date=datetime.utcnow() + timedelta(hours=1)  # 1-hour trial
        )
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'redirect': url_for('dashboard')})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        
        return jsonify({'error': 'Invalid credentials'}), 400
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', projects=projects)

@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()
    
    # Check trial/subscription status
    if current_user.subscription_type == 'free':
        if current_user.trial_end_date and datetime.utcnow() > current_user.trial_end_date:
            return jsonify({'error': 'Trial expired. Please subscribe to continue.'}), 403
        
        # Check project limit for free users
        project_count = Project.query.filter_by(user_id=current_user.id).count()
        if project_count >= 1:
            return jsonify({'error': 'Free trial limited to 1 project. Subscribe for unlimited projects.'}), 403
    
    # Create new project
    project_id = generate_project_id()
    project = Project(
        project_id=project_id,
        user_id=current_user.id,
        name=data['name'],
        description=data['description']
    )
    
    db.session.add(project)
    db.session.commit()
    
    # Create project directory
    create_project_directory(project_id)
    
    # Start simulation
    sim_manager.start_simulation(project_id, current_user.id, data['description'])
    
    return jsonify({
        'success': True,
        'project_id': project_id,
        'redirect': url_for('project_view', project_id=project_id)
    })

@app.route('/project/<project_id>')
@login_required
def project_view(project_id):
    project = Project.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not project:
        return redirect(url_for('dashboard'))
    
    orchestrator = sim_manager.get_simulation(project_id)
    if not orchestrator:
        return redirect(url_for('dashboard'))
    
    return render_template('project.html', project=project, orchestrator=orchestrator)

@app.route('/api/project/<project_id>/status')
@login_required
def project_status(project_id):
    project = Project.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    orchestrator = sim_manager.get_simulation(project_id)
    if not orchestrator:
        return jsonify({'error': 'Simulation not active'}), 404
    
    return jsonify({
        'company_state': orchestrator.company_state,
        'agents': {k: v.to_dict() for k, v in orchestrator.agents.items()},
        'recent_messages': [asdict(msg) for msg in orchestrator.communication_log[-10:]]
    })

@app.route('/api/project/<project_id>/message', methods=['POST'])
@login_required
def send_message(project_id):
    project = Project.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    message = data.get('message', '')
    
    orchestrator = sim_manager.get_simulation(project_id)
    if orchestrator:
        orchestrator.process_owner_request(message)
        sim_manager.save_simulation_state(project_id, orchestrator)
    
    return jsonify({'success': True})

@app.route('/api/project/<project_id>/generate_documents', methods=['POST'])
@login_required
def generate_documents(project_id):
    project = Project.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    try:
        # Generate business plan
        business_plan = generate_business_plan(project)
        business_plan_path = Path(f"user_projects/{project_id}/output/business_plan.md")
        with open(business_plan_path, 'w') as f:
            f.write(business_plan)
        
        # Generate legal documents
        legal_docs = generate_legal_documents(project)
        for filename, content in legal_docs.items():
            legal_path = Path(f"user_projects/{project_id}/output/{filename}")
            with open(legal_path, 'w') as f:
                f.write(content)
        
        # Create document records
        doc = Document(
            project_id=project.id,
            document_type='business_plan',
            file_name='business_plan.md',
            file_path=str(business_plan_path),
            content_hash=hashlib.sha256(business_plan.encode()).hexdigest()
        )
        db.session.add(doc)
        
        for filename in legal_docs.keys():
            legal_path = Path(f"user_projects/{project_id}/output/{filename}")
            doc = Document(
                project_id=project.id,
                document_type='legal_docs',
                file_name=filename,
                file_path=str(legal_path),
                content_hash=hashlib.sha256(legal_docs[filename].encode()).hexdigest()
            )
            db.session.add(doc)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Documents generated successfully'})
    
    except Exception as e:
        logger.error(f"Error generating documents: {e}")
        return jsonify({'error': 'Failed to generate documents'}), 500

@app.route('/api/project/<project_id>/download')
@login_required
def download_project(project_id):
    project = Project.query.filter_by(project_id=project_id, user_id=current_user.id).first()
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Create ZIP file
    import zipfile
    import io
    
    memory_file = io.BytesIO()
    project_path = Path(f"user_projects/{project_id}")
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                arc_name = file_path.relative_to(project_path)
                zf.write(file_path, arc_name)
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'{project.name.replace(" ", "_")}_project.zip'
    )

@app.route('/subscribe')
@login_required
def subscribe():
    return render_template('subscribe.html')

@app.route('/api/create_checkout_session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        # This would integrate with Stripe in production
        # For demo, we'll simulate a successful subscription
        current_user.subscription_type = 'premium'
        current_user.subscription_status = 'active'
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Template filters
@app.template_filter('format_currency')
def format_currency_filter(amount):
    return f"${amount:,.2f}"

@app.template_filter('format_date')
def format_date_filter(date):
    if date:
        return date.strftime('%B %d, %Y')
    return 'N/A'

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)