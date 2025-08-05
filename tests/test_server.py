#!/usr/bin/env python3
"""
Standalone test server for integration tests.
This server can be started independently or by conftest.py
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the project paths
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
src_path = os.path.join(root_dir, "src")

sys.path.insert(0, root_dir)
sys.path.insert(0, src_path)

from web import create_app

def create_test_server(port=5001, debug=False):
    """Create and configure the test server"""
    # Configure for testing with optimizations
    app, socketio = create_app({
        'TESTING': True, 
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': None
    })
    
    # Reduce logging overhead for tests
    if not debug:
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        logging.getLogger('socketio').setLevel(logging.ERROR)
        logging.getLogger('engineio').setLevel(logging.ERROR)
    
    return app, socketio

def main():
    """Main entry point for standalone server"""
    parser = argparse.ArgumentParser(description='Start test server for integration tests')
    parser.add_argument('--port', type=int, default=5001, help='Port to run server on')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode and verbose logging')
    args = parser.parse_args()
    
    app, socketio = create_test_server(port=args.port, debug=args.debug)
    
    print(f"Starting test server on port {args.port}")
    if args.debug:
        print("Debug mode enabled")
    
    try:
        socketio.run(
            app, 
            debug=args.debug, 
            host='127.0.0.1', 
            port=args.port, 
            use_reloader=False,
            log_output=args.debug
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
