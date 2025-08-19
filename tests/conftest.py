#!/usr/bin/env python3
"""
pytest configuration and fixtures for the Bribery game tests

Dependencies:
- pytest (from requirements.txt)
- Flask (from requirements.txt)
- requests (from requirements.txt)
- For UI tests: selenium, webdriver-manager (from requirements-dev.txt)

Setup:
1. py -m pip install -r requirements.txt
2. py -m pip install -r requirements-dev.txt

Troubleshooting:
- If UI tests fail with Selenium errors: Ensure requirements-dev.txt is installed
- If test server fails to start: Check for process using port 5001
- For detailed test architecture, see .github/copilot-instructions.md
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
    # Use a dynamic port to avoid conflicts
    test_port = find_free_port()
    base_url = f'http://127.0.0.1:{test_port}'
    socketio_url = f'http://127.0.0.1:{test_port}'  # Use consistent host
    
    # Start our own server (don't check for existing since we use dynamic ports)
    
    # Use the proper test_server.py file
    server_script_path = os.path.join(os.path.dirname(__file__), 'test_server.py')
    
    server_process = None
    try:
        # Start server process
        venv_python = sys.executable
        startup_info = subprocess.STARTUPINFO()
        startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup_info.wShowWindow = subprocess.SW_HIDE
        
        server_process = subprocess.Popen(
            [venv_python, server_script_path, '--port', str(test_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startup_info,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # Wait for server to start
        max_retries = 30  # Increased timeout for slower machines
        retry_delay = 0.5
        for i in range(max_retries):
            try:
                response = requests.get(base_url, timeout=2.0)  # Increased timeout
                if response.status_code == 200:
                    print(f"✅ Test server started successfully on port {test_port}")
                    break
            except requests.exceptions.RequestException as e:
                if i == max_retries - 1:
                    # Print server output for debugging
                    if server_process.poll() is not None:
                        stdout, stderr = server_process.communicate()
                        print(f"❌ Server process exited with code {server_process.returncode}")
                        print(f"STDOUT: {stdout.decode() if stdout else 'None'}")
                        print(f"STDERR: {stderr.decode() if stderr else 'None'}")
                    server_process.terminate()
                    pytest.fail(f"❌ Test server failed to start within {max_retries * retry_delay} seconds on port {test_port}. Last error: {e}")
                time.sleep(retry_delay)
        
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
                # Use Windows-specific process termination
                try:
                    server_process.send_signal(signal.CTRL_BREAK_EVENT)
                except (OSError, AttributeError):
                    server_process.terminate()
                
                # Wait for process to end, with timeout
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("⚠️ Server didn't terminate gracefully, forcing kill...")
                    if os.name == 'nt':
                        server_process.kill()
                    else:
                        try:
                            os.killpg(os.getpgid(server_process.pid), signal.SIGKILL)
                        except:
                            server_process.kill()
                    server_process.wait()
                    
            except Exception as e:
                print(f"Warning: Error shutting down server: {e}")
        
        # Clean up - no temporary script to remove since we use the proper test_server.py
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
def chrome_driver():
    """Create a Chrome driver for UI tests"""
    from helpers.browser_helpers import BrowserHelper
    
    # Create the driver
    driver = BrowserHelper.create_chrome_driver()
    if not driver:
        pytest.skip("Chrome driver could not be created - UI tests will be skipped")
    
    yield driver
    
    # Clean up
    if driver:
        driver.quit()

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

@pytest.fixture
def socketio_helper_manager(test_server):
    """Create a SocketIO helper manager for testing"""
    try:
        # Import here to avoid import errors when selenium is not installed
        from helpers.socketio_helpers import SocketIOHelperManager
        manager = SocketIOHelperManager(test_server['socketio_url'])
        yield manager
        # Clean up
        manager.disconnect_all()
    except ImportError:
        pytest.skip("SocketIO helper not available - socketio tests will be skipped")
        yield None
