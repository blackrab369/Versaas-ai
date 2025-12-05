#!/usr/bin/env python3
"""
Zero-to-One Virtual Software Inc. - Enterprise Platform Launcher
Professional launcher for the enhanced SaaS platform
"""

import sys
import os
import subprocess
import webbrowser
import threading
import time
import argparse
from pathlib import Path
import platform
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ZTO-Enterprise-Launcher')

def check_postgresql():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("PostgreSQL client found: %s", result.stdout.strip())
            return True
    except FileNotFoundError:
        logger.warning("PostgreSQL client not found. Will use SQLite fallback.")
        return False

def setup_environment():
    """Setup environment variables and directories"""
    env = os.environ.copy()
    
    # Create required directories
    directories = [
        'logs',
        'user_projects',
        'instance',
        'backups',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Set environment variables
    env['FLASK_ENV'] = 'production'
    env['FLASK_DEBUG'] = '0'
    env['ZTO_LOG_LEVEL'] = 'INFO'
    
    # Database configuration
    if check_postgresql():
        # Try to use PostgreSQL
        env['DATABASE_URL'] = 'postgresql://zto_user:zto_password@localhost:5432/zto_enterprise'
        logger.info("Using PostgreSQL database")
    else:
        # Fallback to SQLite
        env['DATABASE_URL'] = 'sqlite:///zto_enterprise.db'
        logger.info("Using SQLite database (PostgreSQL not found)")
    
    return env

def install_dependencies():
    """Install required Python packages"""
    logger.info("Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_enterprise.txt'], 
                      check=True, capture_output=True)
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Failed to install dependencies: %s", e)
        return False

def initialize_database():
    """Initialize the database"""
    logger.info("Initializing database...")
    
    try:
        # Import and initialize database
        sys.path.insert(0, str(Path(__file__).parent))
        from zto_enterprise_platform import app, db
        
        with app.app_context():
            db.create_all()
            logger.info("Database initialized successfully")
            return True
    except Exception as e:
        logger.error("Failed to initialize database: %s", e)
        return False

def create_demo_user():
    """Create a demo user for testing"""
    logger.info("Creating demo user...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from zto_enterprise_platform import app, db, User
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timedelta
        
        with app.app_context():
            # Check if demo user exists
            demo_user = User.query.filter_by(username='demo').first()
            if not demo_user:
                demo_user = User(
                    username='demo',
                    email='demo@zto-inc.com',
                    password_hash=generate_password_hash('demo123'),
                    subscription_type='premium',
                    subscription_status='active',
                    trial_end_date=datetime.utcnow() + timedelta(days=30)
                )
                db.session.add(demo_user)
                db.session.commit()
                logger.info("Demo user created successfully")
            else:
                logger.info("Demo user already exists")
            
            return True
    except Exception as e:
        logger.error("Failed to create demo user: %s", e)
        return False

def launch_web_server(env, port=5000, debug=False):
    """Launch the Flask web server"""
    logger.info("Launching web server on port %d...", port)
    
    try:
        if debug:
            # Development mode with Flask's built-in server
            subprocess.run([sys.executable, 'zto_enterprise_platform.py'], env=env, check=True)
        else:
            # Production mode with Gunicorn
            cmd = [
                'gunicorn',
                '--bind', f'0.0.0.0:{port}',
                '--workers', '4',
                '--worker-class', 'gevent',
                '--worker-connections', '1000',
                '--max-requests', '1000',
                '--max-requests-jitter', '100',
                '--timeout', '30',
                '--keep-alive', '2',
                '--log-level', 'info',
                '--access-logfile', 'logs/access.log',
                '--error-logfile', 'logs/error.log',
                'zto_enterprise_platform:app'
            ]
            subprocess.run(cmd, env=env, check=True)
            
    except subprocess.CalledProcessError as e:
        logger.error("Failed to launch web server: %s", e)
        return False
    except FileNotFoundError:
        # Fallback to Flask development server if Gunicorn not found
        logger.warning("Gunicorn not found, using Flask development server")
        env['FLASK_ENV'] = 'development'
        env['FLASK_DEBUG'] = '1'
        subprocess.run([sys.executable, 'zto_enterprise_platform.py'], env=env, check=True)

def launch_browser(port=5000):
    """Launch browser after server starts"""
    time.sleep(3)  # Wait for server to start
    url = f'http://localhost:{port}'
    logger.info("Opening browser at %s", url)
    webbrowser.open(url)

def show_system_info():
    """Display system information"""
    print("\n" + "="*80)
    print("Zero-to-One Virtual Software Inc. - Enterprise Platform")
    print("="*80)
    print(f"Python Version: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"PostgreSQL: {'Available' if check_postgresql() else 'Not available (using SQLite)'}")
    print("="*80)
    print()

def show_usage_instructions():
    """Show usage instructions"""
    print("\n" + "="*80)
    print("USAGE INSTRUCTIONS")
    print("="*80)
    print("1. Access the web interface at http://localhost:5000")
    print("2. Register for a new account or use the demo account:")
    print("   - Username: demo")
    print("   - Password: demo123")
    print("3. Create your first project and watch the AI team work!")
    print("4. Interact with your CEO through the chat interface")
    print("5. Monitor progress in the 2.5D virtual office")
    print("6. Generate business documents and export your project")
    print()
    print("Features:")
    print("- 25 autonomous AI employees with unique personalities")
    print("- 2.5D virtual office with 32-bit enhanced graphics")
    print("- Real-time character interactions and thought processes")
    print("- Computer system views with live code development")
    print("- Comprehensive business plan generation")
    print("- Persistent simulations that run 24/7")
    print("- Multiple project support")
    print("- Professional financial dashboard")
    print("="*80)
    print()

def main():
    parser = argparse.ArgumentParser(description='Launch Zero-to-One Virtual Software Inc. Enterprise Platform')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    parser.add_argument('--setup-only', action='store_true', help='Only perform setup, don\'t start server')
    parser.add_argument('--demo-data', action='store_true', help='Create demo data')
    
    args = parser.parse_args()
    
    # Show system information
    show_system_info()
    
    # Setup environment
    env = setup_environment()
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        return 1
    
    # Initialize database
    if not initialize_database():
        logger.error("Failed to initialize database")
        return 1
    
    # Create demo user if requested
    if args.demo_data:
        if not create_demo_user():
            logger.error("Failed to create demo user")
            return 1
    
    # If setup only, exit here
    if args.setup_only:
        logger.info("Setup completed successfully")
        return 0
    
    # Launch browser in separate thread
    if not args.no_browser:
        browser_thread = threading.Thread(target=launch_browser, args=(args.port,))
        browser_thread.daemon = True
        browser_thread.start()
    
    # Launch web server
    try:
        launch_web_server(env, args.port, args.debug)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        print("\nThank you for using Zero-to-One Virtual Software Inc.!")
        return 0
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return 1
    
    return 0

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)