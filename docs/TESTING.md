# Running Integration Tests

This document explains how to run the integration tests for the Bribery game.

## Prerequisites

Make sure you have all the required dependencies installed:

```powershell
# Install all dependencies
py -m pip install -r requirements.txt -r requirements-dev.txt

# Verify dependencies are correctly installed
py scripts\verify_test_deps.py
```

## Understanding Test Types

We use different types of tests with different philosophies:

1. **Unit Tests**: Fast, isolated tests that verify individual components
   - Run with: `py -m pytest tests/unit/`
   - Time: ~0.69 seconds

2. **Integration Tests**: Tests that verify multiple components work together
   - Run with: `py -m pytest tests/integration/`
   - Time: ~30 seconds
   - **Note**: These tests use the SocketIO helper to simulate real-time communication

3. **Static Analysis Tests**: Tests that verify code structure without execution
   - Example: `tests/unit/test_auto_submission.py` verifies JavaScript implementation

4. **Manual Testing**: For complex UI interactions during development

## SocketIO Testing

For integration tests that use SocketIO:

1. Make sure `python-socketio` is installed (via requirements.txt)
2. Use the `MultiPlayerHelper` class to create players and games
3. Don't use UI-driven tests (Selenium) as they're too brittle

## Troubleshooting

If you see `SocketIO helper not available` errors:

1. Verify dependencies with `py scripts\verify_test_deps.py`
2. Check that your Python environment has access to the internet
3. Make sure the test server is able to start on port 5001 (no conflicts)

## Common Examples

```powershell
# Run all tests
py -m pytest

# Run unit tests only (fast)
py -m pytest tests/unit/

# Run integration tests only
py -m pytest tests/integration/

# Run a specific test file
py -m pytest tests/unit/test_auto_submission.py -v

# Run a specific test function
py -m pytest tests/integration/test_auto_submission_integration.py::test_auto_submission_integration -v
```
