# Bribery Game

Flask-SocketIO multiplayer game where players submit creative bribes and vote on submissions.

## Quick Start
```bash
# Production setup
pip install -r requirements.txt
py -m flask run

# Development setup (includes code quality tools)
pip install -r requirements.txt -r requirements-dev.txt
py -m pre_commit install  # Optional: enable git hooks
```

## Code Quality
```bash
# Run all quality checks
py scripts\quality_check.py

# Auto-fix formatting issues
scripts\fix_quality.bat

# Individual tools
py -m flake8 src/          # Linting
py -m black src/           # Code formatting  
py -m isort src/           # Import sorting
py -m mypy src/            # Type checking
py -m bandit -r src/       # Security scan
```

## Testing
```powershell
# Install ALL test dependencies first
py -m pip install -r requirements.txt
py -m pip install -r requirements-dev.txt

# Run tests
py -m pytest                # Full suite
py -m pytest tests/unit/    # Unit tests (fastest)
py -m pytest tests/integration/  # Integration tests
```

## Key Features
- **Mobile-Optimised**: Touch-friendly interface with mobile image upload
- **Custom Time Settings**: Flexible timer configuration for different group sizes  
- **Real-Time Progress**: Live tracking of submission and voting progress
- **Custom Prompts**: Players choose their own prompts (default enabled)
- **4-Character Game Codes**: Easy-to-share codes for joining games
- **Multiple Input Types**: Text, images, links, and GIFs supported

## Architecture
- **Backend:** Flask + SocketIO for real-time multiplayer
- **Frontend:** Responsive HTML/CSS/JS with mobile-first design
- **Testing:** Comprehensive unit and integration test coverage

See `.copilot-instructions.md` for development context.
