#!/usr/bin/env python3
"""
Main application entry point for the Bribery game server
"""

import os
import sys
import threading
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from web import create_app
from web.socket_handlers import get_game_manager


def cleanup_games():
    """Periodically clean up empty games"""
    game_manager = get_game_manager()
    if game_manager:
        game_manager.cleanup_empty_games()
    # Schedule next cleanup
    threading.Timer(300.0, cleanup_games).start()  # Every 5 minutes


def start_cleanup_timer():
    """Start the cleanup timer - only call when running the server"""
    cleanup_games()


def main():
    """Main application entry point"""
    # Create the Flask app and SocketIO instance
    app, socketio = create_app()
    
    # Start the cleanup timer when running as main
    start_cleanup_timer()
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Starting Bribery game server on {host}:{port}")
    print(f"📁 Debug mode: {debug}")
    
    # Run the application
    socketio.run(app, debug=debug, host=host, port=port)


if __name__ == '__main__':
    main()
