#!/usr/bin/env python3
"""
pytest configuration and fixtures for the Bribery game tests
"""

import pytest
import threading
import time
import requests
from contextlib import contextmanager
import sys
import os
import socket
import subprocess
import signal

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

def find_free_port():
    """Find a free port to use for testing"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

@pytest.fixture(scope="session")
def test_server():
    """Start or connect to a Flask test server for the entire test session"""
    # First, try to find if a server is already running
    test_port = 5001  # Use a fixed port for test server
    base_url = f'http://127.0.0.1:{test_port}'
    socketio_url = f'http://localhost:{test_port}'
    
    # Check if a server is already running
    try:
        response = requests.get(base_url, timeout=1)
        if response.status_code == 200:
            print(f"✅ Found existing test server on port {test_port}")
            server_info = {
                'base_url': base_url,
                'socketio_url': socketio_url,
                'port': test_port,
                'managed_by_us': False
            }
            yield server_info
            return
    except requests.exceptions.RequestException:
        pass  # No server running, we'll start one
    
    # No server running, start our own
    server_script = f'''
import sys
import os
from pathlib import Path

# Add paths
root_dir = r"{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}"
src_path = os.path.join(root_dir, "src")
sys.path.insert(0, root_dir)
sys.path.insert(0, src_path)

from web import create_app

# Configure for testing with optimizations
app, socketio = create_app({{
    'TESTING': True, 
    'SECRET_KEY': 'test-secret-key',
    'WTF_CSRF_ENABLED': False,
    'SERVER_NAME': None
}})

# Reduce logging overhead
import logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

if __name__ == "__main__":
    print(f"Starting test server on port {test_port}")
    socketio.run(app, debug=False, host='127.0.0.1', port={test_port}, use_reloader=False, log_output=False)
'''
    
    # Write the server script to a temporary file
    script_path = os.path.join(os.path.dirname(__file__), 'test_server_temp.py')
    with open(script_path, 'w') as f:
        f.write(server_script)
    
    server_process = None
    try:
        # Start server process
        venv_python = r"C:/Users/AB018M1/OneDrive - Absa/Code/GameExperiment/.venv/Scripts/python.exe"
        server_process = subprocess.Popen(
            [venv_python, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        # Wait for server to start
        max_retries = 15
        for i in range(max_retries):
            try:
                response = requests.get(base_url, timeout=0.5)
                if response.status_code == 200:
                    print(f"✅ Test server started successfully on port {test_port}")
                    break
            except requests.exceptions.RequestException:
                if i == max_retries - 1:
                    server_process.terminate()
                    pytest.fail(f"❌ Test server failed to start within 15 seconds on port {test_port}")
                time.sleep(0.5)
        
        # Provide server info to tests
        server_info = {
            'base_url': base_url,
            'socketio_url': socketio_url,
            'port': test_port,
            'managed_by_us': True
        }
        
        yield server_info
        
    finally:
        # Only cleanup if we started the server
        if server_process:
            print("🧹 Shutting down test server...")
            try:
                if os.name == 'nt':  # Windows
                    server_process.send_signal(signal.CTRL_BREAK_EVENT)
                else:  # Unix-like
                    server_process.terminate()
                
                # Wait for process to end, with timeout
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()  # Force kill if it doesn't terminate gracefully
                    server_process.wait()
                    
            except Exception as e:
                print(f"Warning: Error shutting down server: {e}")
        
        # Clean up temporary script
        try:
            os.remove(script_path)
        except Exception:
            pass

@pytest.fixture(autouse=True)
def clean_game_state():
    """Clean game state before and after each test"""
    # The game state cleanup needs to happen on the server side, not client side
    # Since we can't import Flask modules from the test process, we'll use a different approach
    
    # Before test: Let each test start fresh by using unique game IDs and players
    yield
    
    # After test: The game cleanup happens when SocketIO clients disconnect
    # and when the server session ends. No additional cleanup needed here.

@pytest.fixture
def game_manager_instance():
    """Provide access to the game manager for tests"""
    try:
        from web.socket_handlers import get_game_manager
        return get_game_manager()
    except ImportError:
        return None

@contextmanager
def suppress_socketio_logs():
    """Suppress verbose SocketIO logs during testing"""
    import logging
    
    # Set logging levels to reduce noise
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    try:
        yield
    finally:
        # Restore logging levels
        logging.getLogger('socketio').setLevel(logging.INFO)
        logging.getLogger('engineio').setLevel(logging.INFO)
        logging.getLogger('werkzeug').setLevel(logging.INFO)

# Configure pytest to use the socketio log suppression
@pytest.fixture(autouse=True)
def suppress_logs():
    """Automatically suppress verbose logs for all tests"""
    with suppress_socketio_logs():
        yield
