@echo off
REM Start the test server for manual testing and debugging
echo Starting test server for manual testing...
echo Press Ctrl+C to stop
echo.
py tests\test_server.py --port 5001 --debug
