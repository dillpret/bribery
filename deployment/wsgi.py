#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Import from our refactored structure
from web import create_app
from web.socket_handlers import get_game_manager
import threading


def cleanup_games():
    """Periodically clean up empty games"""
    game_manager = get_game_manager()
    if game_manager:
        game_manager.cleanup_empty_games()
    # Schedule next cleanup
    threading.Timer(300.0, cleanup_games).start()  # Every 5 minutes


def start_cleanup_timer():
    """Start the cleanup timer for production"""
    cleanup_games()


# Create the Flask app and SocketIO instance
app, socketio = create_app()

# Start cleanup timer for production deployment
start_cleanup_timer()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Starting Bribery game server on 0.0.0.0:{port}")
    print(f"📁 Debug mode: {debug}")
    print("🧹 Cleanup timer started")
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)
