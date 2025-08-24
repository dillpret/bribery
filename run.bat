@echo off
REM Bribery Game Launcher
REM This batch file runs the Bribery game without requiring PowerShell script execution

echo Checking for virtual environment...

REM Check for venv in common locations from project root
IF EXIST venv\Scripts\activate.bat (
    echo Activating virtual environment (venv)...
    call venv\Scripts\activate.bat
    goto :runapp
)

IF EXIST .venv\Scripts\activate.bat (
    echo Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
    goto :runapp
)

IF EXIST env\Scripts\activate.bat (
    echo Activating virtual environment (env)...
    call env\Scripts\activate.bat
    goto :runapp
)

echo No virtual environment found. Running with system Python...

:runapp
echo Installing dependencies...
py -m pip install -r requirements.txt

echo.
echo Starting Bribery Game Server...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the application directly
py app.py
pause