"""
Web package for Flask application and Socket.IO handlers
"""

from .app import create_app
from .routes import register_routes
from .socket_handlers import register_socket_handlers

__all__ = ['create_app', 'register_socket_handlers', 'register_routes']
