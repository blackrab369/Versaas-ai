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
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ZTO-SaaS')

from config import config

# Add project path for ZTO Kernel
# We use the config BASE_DIR to ensure reliability
sys.path.append(str(Path(__file__).parent / 'ZTO_Projects' / 'ZTO_Demo'))
from zto_kernel import get_orchestrator, ZTOOrchestrator

# Initialize Flask app
app = Flask(__name__)
# Load config based on environment
env_name = os.getenv('FLASK_ENV', 'default')
app.config.from_object(config[env_name])

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
    campaigns = db.relationship('AdCampaign', backref='user', lazy=True)

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
    payment_type = db.Column(db.String(20), nullable=False)  # subscription, project_premium, ads
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdSpace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    ad_type = db.Column(db.String(20), default='banner')  # banner, keyword
    price_per_day = db.Column(db.Float, default=10.0)
    description = db.Column(db.String(200))

class AdCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ad_space_id = db.Column(db.Integer, db.ForeignKey('ad_space.id'), nullable=False)
    keyword = db.Column(db.String(100), nullable=True)  # Only for keyword ads
    content_url = db.Column(db.String(500), nullable=False)  # Image URL or Text content
    target_url = db.Column(db.String(500), nullable=False)   # Where ad clicks go
    
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    
    # Analytics
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    
    ad_space = db.relationship('AdSpace', backref='campaigns')


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

# Dummy generators removed. Using Orchestrator methods.

# Routes
@app.route('/')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about-virsaas')
def about_virsaas():
    return render_template('about_virsaas.html')


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
        # Get active orchestrator
        orchestrator = sim_manager.get_simulation(project_id)
        if not orchestrator:
            return jsonify({'error': 'Simulation not active - cannot generate documents'}), 400

        # Generate business plan via AI Service
        business_plan = orchestrator.generate_business_plan(project.name, project.description)
        business_plan_path = Path(f"user_projects/{project_id}/output/business_plan.md")
        # Ensure output dir exists
        business_plan_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(business_plan_path, 'w') as f:
            f.write(business_plan)
        
        # Generate legal documents via AI Service
        legal_docs = orchestrator.generate_legal_documents(project.name)
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

# --- Ads Service Routes ---

@app.route('/ads')
@login_required
def ads_dashboard():
    campaigns = AdCampaign.query.filter_by(user_id=current_user.id).all()
    available_spaces = AdSpace.query.all()
    
    # Ensure default spaces exist if empty
    if not available_spaces:
        defaults = [
            AdSpace(name="Home Top Banner", slug="home-top", ad_type="banner", price_per_day=50.0, description="Prime visibility on homepage"),
            AdSpace(name="Sidebar Feature", slug="sidebar-feat", ad_type="banner", price_per_day=25.0, description="Sticky sidebar on dashboard"),
            AdSpace(name="Keyword Sponsor", slug="keyword", ad_type="keyword", price_per_day=5.0, description="Target specific search keywords")
        ]
        for d in defaults:
            db.session.add(d)
        db.session.commit()
        available_spaces = AdSpace.query.all()
        
    return render_template('ads_dashboard.html', campaigns=campaigns, spaces=available_spaces)

@app.route('/ads/purchase', methods=['GET', 'POST'])
@login_required
def ads_purchase():
    if request.method == 'POST':
        space_id = request.form.get('space_id')
        days = int(request.form.get('days', 7))
        content_url = request.form.get('content_url')
        target_url = request.form.get('target_url')
        keyword = request.form.get('keyword')
        
        space = AdSpace.query.get(space_id)
        if not space:
            return jsonify({'error': 'Invalid ad space'}), 400
            
        amount = space.price_per_day * days
        
        # Simulate Stripe Payment
        payment = Payment(
            project_id=0, # System payment
            stripe_payment_id=f"ad_pay_{uuid.uuid4()}",
            amount=amount,
            payment_type='ads',
            status='succeeded'
        )
        # Hack: Payment model requires project_id but this is user-level. 
        # Ideally we refactor Payment to make project_id nullable or use a user_payment table.
        # For now we use the first project of user or dummy.
        first_project = Project.query.filter_by(user_id=current_user.id).first()
        payment.project_id = first_project.id if first_project else 0
        
        db.session.add(payment)
        
        # Create Campaign
        campaign = AdCampaign(
            user_id=current_user.id,
            ad_space_id=space.id,
            keyword=keyword if space.ad_type == 'keyword' else None,
            content_url=content_url,
            target_url=target_url,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=days),
            status='active'
        )
        db.session.add(campaign)
        db.session.commit()
        
        return jsonify({'success': True, 'redirect': url_for('ads_dashboard')})
        
    space_id = request.args.get('space_id')
    selected_space = AdSpace.query.get(space_id) if space_id else None
    spaces = AdSpace.query.all()
    return render_template('ads_purchase.html', spaces=spaces, selected_space=selected_space)


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