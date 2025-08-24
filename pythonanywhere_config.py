"""
Jarvis 2.0 - PythonAnywhere Deployment Configuration
This file helps configure Jarvis for PythonAnywhere's free tier
"""

import os
import sys
from pathlib import Path

# PythonAnywhere specific configuration
PYTHONANYWHERE = True

# Add the current directory to Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Environment configuration for PythonAnywhere
def configure_environment():
    """Configure environment variables for PythonAnywhere"""

    # Set default environment variables if not set
    env_defaults = {
        'FLASK_ENV': 'production',
        'FLASK_APP': 'web_app.py',
        'PORT': '8080',  # PythonAnywhere default port
        'PYTHONUNBUFFERED': '1',
        'ENCRYPTION_KEY': 'jarvis_pa_default_key_2024',
        'JWT_SECRET_KEY': 'jarvis_pa_jwt_secret_2024',
        'BLOCKCHAIN_DIFFICULTY': '2',  # Lower difficulty for free tier
        'QUANTUM_SIMULATION_ENABLED': 'false',  # Disable quantum for free tier
        'LOG_LEVEL': 'INFO'
    }

    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value

    # Configure database for PythonAnywhere (SQLite for free tier)
    if 'DATABASE_URL' not in os.environ:
        db_path = current_dir / 'jarvis_database.db'
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

    # Configure Google API Key (user must set this)
    if 'GOOGLE_API_KEY' not in os.environ:
        print("⚠️  WARNING: GOOGLE_API_KEY not set!")
        print("   Please set your Google API key in PythonAnywhere environment variables")
        print("   Web -> Variables in your PythonAnywhere dashboard")

# Configure for PythonAnywhere
configure_environment()

# WSGI application for PythonAnywhere
def application(environ, start_response):
    """WSGI application for PythonAnywhere"""

    # Add the app directory to Python path
    app_dir = Path(__file__).parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    # Import and configure the Flask app
    from web_app import app

    # Configure app for PythonAnywhere
    app.config.update(
        SERVER_NAME=None,
        DEBUG=False,
        TESTING=False
    )

    # Return the WSGI app
    return app(environ, start_response)

# For direct running (development)
if __name__ == '__main__':
    from web_app import app
    app.run(host='0.0.0.0', port=8080)
