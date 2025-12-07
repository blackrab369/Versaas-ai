#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. – Enterprise Platform Launcher
Vercel / Supabase compatible edition
"""
import redis
import argparse
import logging
import os
import platform
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ZTO-Enterprise-Launcher')


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def check_postgresql():
    """Return True if psql client is available."""
    try:
        r = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        return r.returncode == 0
    except FileNotFoundError:
        return False


def get_database_url():
    """
    1. Use DATABASE_URL if provided (Vercel / Supabase / local export).
    2. Otherwise fall back to local PostgreSQL.
    3. Otherwise fall back to SQLite.
    """
    if os.getenv("DATABASE_URL"):
        logger.info("Using DATABASE_URL from environment")
        return os.getenv("DATABASE_URL")

    if check_postgresql():
        logger.info("No DATABASE_URL env-var; using local PostgreSQL")
        return "postgresql://zto_user:zto_password@localhost:5432/zto_enterprise"

    logger.info("PostgreSQL not found; using SQLite fallback")
    return "sqlite:///zto_enterprise.db"


def setup_environment():
    """Prepare env dict for sub-processes."""
    env = os.environ.copy()
    
    global redis_client
    REDIS_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
    res = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else "redis://localhost:6379/0"
    redis_client = res if REDIS_URL else "redis://localhost:6379/0"
    
    #redis_url = os.getenv("UPSTASH_REDIS_REST_URL") or ""
    #redis_client = redis.from_url(redis_url, decode_responses=True) if redis_url and redis_url.startswith("redis") else None

    # ensure runtime dirs exist
    for d in ('logs', 'user_projects', 'instance', 'backups', 'temp'):
        Path(d).mkdir(exist_ok=True)

    # Flask / ZTO flags
    env['FLASK_ENV'] = os.getenv('FLASK_ENV', 'production')
    env['FLASK_DEBUG'] = os.getenv('FLASK_DEBUG', '0')
    env['ZTO_LOG_LEVEL'] = os.getenv('ZTO_LOG_LEVEL', 'INFO')
    #env['ZTO_REDIS_URL'] = str(redis_client)  # redis client URL

    # database
    env['DATABASE_URL'] = get_database_url()
    return env


def install_deps():
    """pip install -r requirements_enterprise.txt"""
    logger.info("Installing dependencies …")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements_enterprise.txt'],
            check=True, capture_output=True
        )
        logger.info("Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Dependency install failed: %s", e)
        return False


# ------------------------------------------------------------------
# DB initialisation (works locally OR against remote Supabase)
# ------------------------------------------------------------------
def init_db():
    """Create tables via SQLAlchemy."""
    logger.info("Initialising database …")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from zto_enterprise_platform import app, db

        with app.app_context():
            db.create_all()
        logger.info("Database initialised")
        return True
    except Exception as e:
        import traceback
        logger.error("DB init failed: %s", e)
        logger.error("Full traceback:\n%s", traceback.format_exc())  # ← print full stack
        return False


def create_demo_user():
    """Insert demo / seed user."""
    logger.info("Creating demo user …")
    try:
        from zto_enterprise_platform import app, db, User
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timedelta

        with app.app_context():
            if User.query.filter_by(username='demo').first():
                logger.info("Demo user already exists")
                return True

            demo = User(
                username='demo',
                email='demo@zto-inc.com',
                password_hash=generate_password_hash('demo123'),
                subscription_type='premium',
                subscription_status='active',
                trial_end_date=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(demo)
            db.session.commit()
            logger.info("Demo user created")
            return True
    except Exception as e:
        logger.error("Demo user creation failed: %s", e)
        return False


# ------------------------------------------------------------------
# Server launch (local only – Vercel ignores this path)
# ------------------------------------------------------------------
def launch_gunicorn(env, port=5000):
    """Production: gunicorn gevent workers."""
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


def launch_dev(env, port=5000):
    """Development: Flask built-in server."""
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = '1'
    subprocess.run([sys.executable, 'zto_enterprise_platform.py'], env=env, check=True)


def launch_browser(port):
    time.sleep(3)
    url = f'http://localhost:{port}'
    logger.info("Opening browser → %s", url)
    webbrowser.open(url)


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description='Launch ZTO Enterprise Platform')
    p.add_argument('--port', type=int, default=5000)
    p.add_argument('--debug', action='store_true')
    p.add_argument('--no-browser', action='store_true')
    p.add_argument('--setup-only', action='store_true',
                   help='Local setup + exit')
    p.add_argument('--setup-remote', action='store_true',
                   help='Initialise remote DB (Supabase) then exit – use this from your laptop after Vercel deploy')
    p.add_argument('--demo-data', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()

    # banner
    print('\n' + '=' * 80)
    print('Virsaas Virtual Software Inc. – Enterprise Platform')
    print(f'Python {platform.python_version()}  |  DB: {get_database_url().split(":", 1)[0]}')
    print('=' * 80 + '\n')

    env = setup_environment()

    if not install_deps():
        return 1
    if not init_db():
        return 1
    if args.demo_data:
        if not create_demo_user():
            return 1

    # remote-setup mode (run locally but against Supabase)
    if args.setup-remote:
        logger.info("Remote database setup complete – exiting")
        return 0

    # local setup-only mode
    if args.setup-only:
        logger.info("Local setup complete – exiting")
        return 0

    # launch browser thread
    if not args.no_browser:
        t = threading.Thread(target=launch_browser, args=(args.port,), daemon=True)
        t.start()

    # run server
    try:
        if args.debug:
            launch_dev(env, args.port)
        else:
            launch_gunicorn(env, args.port)
    except KeyboardInterrupt:
        logger.info("Shutdown requested – bye!")
        return 0
    except Exception as e:
        logger.error("Server error: %s", e)
        return 1


if __name__ == '__main__':
    sys.exit(main())