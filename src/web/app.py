"""
Flask application factory and configuration
"""

import logging
import os

from flask import Flask
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__,
                template_folder='../../templates',
                static_folder='../../static')

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY', 'your-secret-key-change-this-in-production')
        
    # Ensure static files aren't cached on production
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Add version-based cache busting to static URLs
    @app.context_processor
    def inject_version():
        # Get version from app config (set in routes.py)
        def versioned_static(filename):
            version = app.config.get('VERSION', '1')
            return f"/static/{filename}?v={version}"
        return dict(versioned_static=versioned_static)

    if config:
        app.config.update(config)

    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")

    # Register routes and socket handlers
    from .routes import register_routes
    from .socket_handlers import register_socket_handlers

    register_routes(app)
    register_socket_handlers(socketio)

    return app, socketio
