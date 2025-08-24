#!/usr/bin/env python3
"""
Verify that all required dependencies for tests are installed.
This script helps diagnose issues with test failures due to missing dependencies.

Usage: 
    py scripts\verify_test_deps.py

Test Philosophy:
- We use SocketIO for integration tests rather than UI/Selenium tests
- UI tests are brittle and difficult to maintain
- Socket-based tests provide more reliable validation of game functionality

Common Issues:
- "SocketIO helper not available" error: Run this script to verify dependencies
- Test server fails to start: Check if port 5001 is in use
- Slow tests: Use -v flag for more verbose output to identify bottlenecks
"""

import subprocess
import sys
import importlib.util
import os

def check_dependency(module_name, pip_package=None):
    """Check if a dependency is installed"""
    if pip_package is None:
        pip_package = module_name
        
    print(f"Checking for {module_name}...", end="")
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print(f" ✅ Found")
        return True
    else:
        print(f" ❌ Missing")
        print(f"   Install with: py -m pip install {pip_package}")
        return False

def main():
    """Main function to check dependencies"""
    print("Checking test dependencies...\n")
    
    # Basic requirements from requirements.txt
    all_installed = True
    all_installed &= check_dependency("flask")
    all_installed &= check_dependency("flask_socketio")
    all_installed &= check_dependency("socketio", "python-socketio")
    all_installed &= check_dependency("engineio", "python-engineio")
    all_installed &= check_dependency("pytest")
    all_installed &= check_dependency("requests")
    
    # Development requirements
    all_installed &= check_dependency("pytest_cov", "pytest-cov")
    all_installed &= check_dependency("pytest_mock", "pytest-mock")
    
    if all_installed:
        print("\nAll dependencies installed! ✅")
        print("You should be able to run tests with: py -m pytest")
    else:
        print("\nSome dependencies are missing. ❌")
        print("Install all dependencies with: py -m pip install -r requirements.txt -r requirements-dev.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
