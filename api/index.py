from http.server import BaseHTTPRequestHandler
import os
import sys

# Add project root to sys.path to allow importing modules from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
# Changing from zto_enterprise_platform to zto_saas_platform since that's where we added features
from zto_saas_platform import app

# Vercel needs the variable 'app' to be the Flask instance
# It is already named 'app' in zto_saas_platform.py