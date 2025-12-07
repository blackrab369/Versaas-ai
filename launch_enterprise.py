#!/usr/bin/env python3
"""
Virsaas Virtual Software Inc. – Enterprise Platform Launcher
Vercel / Supabase / SQLite / Redis compatible edition
No syntax traps, no grey hairs.
"""
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

import redis
from dotenv import load_dotenv  # <-- you forgot this

load_dotenv()  # safe even if .env missing

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger('ZTO-Enterprise-Launcher')

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def check_postgresql():
    try:
        return subprocess.run(['psql', '--version'], capture_output=True, text=True).returncode == 0
    except FileNotFoundError:
        return False


def get_database_url():
    """1. env  2. local postgres  3. sqlite"""
    if url := os.getenv("DATABASE_URL"):
        logger.info("Using DATABASE_URL from environment")
        return url
    if check_postgresql():
        logger.info("No DATABASE_URL; using local PostgreSQL")
        return "postgresql://zto_user:zto_password@localhost:5432/zto_enterprise"
    logger.info("PostgreSQL not found; using SQLite fallback")
    return "sqlite:///zto_enterprise.db"


def setup_environment():
    """Prepare env dict for sub-processes."""
    env = os.environ.copy()

    # Redis client (safe)
    redis_url = os.getenv("UPSTASH_REDIS_REST_URL", "redis://localhost:6379/0")
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True) if redis_url.startswith("redis") else None
        redis_client.ping()  # throws if unreachable
    except Exception as e:
        logger.warning("Redis unreachable – running without: %s", e)
        redis_client = None
    env["ZTO_REDIS_URL"] = redis_url

    # runtime dirs
    for d in ("logs", "user_projects", "instance", "backups", "temp"):
        Path(d).mkdir(exist_ok=True)

    # Flask flags
    env["FLASK_ENV"] = os.getenv("FLASK_ENV", "production")
    env["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG", "0")
    env["ZTO_LOG_LEVEL"] = os.getenv("ZTO_LOG_LEVEL", "INFO")

    # database
    env["DATABASE_URL"] = get_database_url()
    return env


def install_deps():
    """pip install -r requirements_enterprise.txt"""
    logger.info("Installing dependencies …")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements_enterprise.txt"],
            check=True, capture_output=True, text=True
        )
        logger.info("Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Dependency install failed: %s", e.stderr)
        return False


# ------------------------------------------------------------------
# DB initialisation (with retry for remote)
# ------------------------------------------------------------------
def init_db(retries: int = 3, delay: int = 2):
    """Create tables via SQLAlchemy."""
    logger.info("Initialising database …")
    for attempt in range(1, retries + 1):
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from zto_enterprise_platform import app, db

            with app.app_context():
                db.create_all()
            logger.info("Database initialised")
            return True
        except Exception as e:
            logger.warning("DB init attempt %s failed: %s", attempt, e)
            if attempt < retries:
                time.sleep(delay)
            else:
                logger.error("Database initialisation failed after %s attempts – exiting", retries)
                return False


def create_demo_user():
    """Insert demo user."""
    logger.info("Creating demo user …")
    try:
        from zto_enterprise_platform import app, db, User
        from werkzeug.security import generate_password_hash
        from datetime import datetime, timedelta

        with app.app_context():
            if User.query.filter_by(username="demo").first():
                logger.info("Demo user already exists")
                return True
            demo = User(
                username="demo",
                email="demo@zto-inc.com",
                password_hash=generate_password_hash("demo123"),
                subscription_type="premium",
                subscription_status="active",
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
# Server launch
# ------------------------------------------------------------------
def launch_gunicorn(env, port=5000):
    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "4",
        "--worker-class", "gevent",
        "--worker-connections", "1000",
        "--max-requests", "1000",
        "--max-requests-jitter", "100",
        "--timeout", "30",
        "--keep-alive", "2",
        "--log-level", "info",
        "--access-logfile", "logs/access.log",
        "--error-logfile", "logs/error.log",
        "zto_enterprise_platform:app"
    ]
    subprocess.run(cmd, env=env, check=True)


def launch_dev(env, port=5000):
    env["FLASK_ENV"] = "development"
    env["FLASK_DEBUG"] = "1"
    subprocess.run([sys.executable, "zto_enterprise_platform.py"], env=env, check=True)


def launch_browser(port):
    time.sleep(3)
    url = f"http://localhost:{port}"
    logger.info("Opening browser → %s", url)
    webbrowser.open(url)


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Launch ZTO Enterprise Platform")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--debug", action="store_true")
    p.add_argument("--no-browser", action="store_true")
    p.add_argument("--no-deps", action="store_true", help="skip pip install")
    p.add_argument("--setup-only", action="store_true", help="init DB + exit")
    p.add_argument("--setup-remote", action="store_true", help="init remote DB + exit")
    p.add_argument("--demo-data", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    print("\n" + "=" * 80)
    print("Virsaas Virtual Software Inc. – Enterprise Platform")
    print(f"Python {platform.python_version()}  |  DB: {get_database_url().split(':', 1)[0]}")
    print("=" * 80 + "\n")

    env = setup_environment()

    if not args.no_deps and not install_deps():
        return 1
    if not init_db():
        return 1
    if args.demo_data and not create_demo_user():
        return 1

    if args.setup_remote:
        logger.info("Remote database setup complete – exiting")
        return 0
    if args.setup_only:
        logger.info("Local setup complete – exiting")
        return 0

    if not args.no_browser:
        threading.Thread(target=launch_browser, args=(args.port,), daemon=True).start()

    try:
        launch_dev(env, args.port) if args.debug else launch_gunicorn(env, args.port)
    except KeyboardInterrupt:
        logger.info("Shutdown requested – bye!")
        return 0
    except Exception as e:
        logger.error("Server error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())