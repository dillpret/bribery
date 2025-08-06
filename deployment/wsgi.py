#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import sys
from pathlib import Path

# Get absolute paths to ensure they work regardless of working directory
wsgi_file = Path(__file__).resolve()
project_root = wsgi_file.parent.parent
src_path = project_root / 'src'

# Debug info (will appear in Gunicorn logs)
print(f"WSGI Debug Info:")
print(f"  WSGI file: {wsgi_file}")
print(f"  Project root: {project_root}")
print(f"  Src path: {src_path}")
print(f"  Current working directory: {Path.cwd()}")

# Add paths to Python path (insert at beginning to prioritise)
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"  Updated sys.path: {sys.path[:5]}")

# Verify the web module exists before importing
web_init_file = src_path / 'web' / '__init__.py'
print(f"  Web module path: {web_init_file}")
print(f"  Web module exists: {web_init_file.exists()}")

if web_init_file.exists():
    try:
        # Import from our refactored structure
        from web import create_app
        from web.socket_handlers import get_game_manager
        import threading
        print("✅ Successfully imported web modules")
        
    except ImportError as e:
        print(f"❌ Import error despite file existing: {e}")
        print(f"❌ This suggests a dependency or sub-import issue")
        
        # Try to import the specific files to narrow down the issue
        try:
            import web
            print(f"✅ Base web module imported successfully")
        except ImportError as e2:
            print(f"❌ Base web module import failed: {e2}")
            
        try:
            from web import app
            print(f"✅ web.app imported successfully")
        except ImportError as e3:
            print(f"❌ web.app import failed: {e3}")
            
        raise e
else:
    print(f"❌ Web module __init__.py not found at expected location")
    print("Available files in src/web/:")
    if (src_path / 'web').exists():
        for file in (src_path / 'web').iterdir():
            print(f"  - {file.name}")
    raise ImportError(f"Web module not found at {web_init_file}")


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
