@echo off
REM Quick quality check and auto-fix script for Windows
echo 🚀 Running code quality fixes...

echo.
echo 🔧 Auto-formatting with Black...
py -m black --line-length=120 src/

echo.
echo 📦 Organizing imports with isort...
py -m isort --profile=black src/

echo.
echo 🔍 Running flake8 check...
py -m flake8 src/ --max-line-length=120 --ignore=E501,W503,E203

echo.
echo 🧪 Running quick unit tests...
py -m pytest tests/unit/ --tb=short -q

echo.
echo ✅ Quality fixes complete!
pause
