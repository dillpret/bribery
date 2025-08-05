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
```bash
py -m pytest                # Full suite (~30s)
py -m pytest tests/unit/    # Unit tests (0.69s)
py -m pytest tests/ui/      # Browser tests (~2min)
```

## Project Status
- ✅ **Performance:** Optimized test suite (10min → 30s)
- ✅ **Architecture:** Modular components (1000+ lines → 95 lines)
- ✅ **Mobile:** Responsive design with touch optimization
- ✅ **Code Quality:** Automated enforcement (130+ violations → 0)
- ✅ **Security:** Input validation and automated scanning
- ⚠️ **Production:** Database persistence and scalability needed

## Architecture
- **Backend:** Flask + SocketIO
- **Frontend:** Modular HTML/CSS/JS components
- **Testing:** 3-tier optimized suite
- **Mobile:** Touch-first responsive design

See `.copilot-instructions.md` for development context.
