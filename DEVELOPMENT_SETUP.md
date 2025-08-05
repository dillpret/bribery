# Development Setup Guide

This guide helps you set up the Bribery Game project for development with all quality tools.

## Quick Setup

### 1. Clone and Install Dependencies
```powershell
# Clone the repository (if not already done)
git clone <repository-url>
cd GameExperiment

# Install production dependencies
py -m pip install -r requirements.txt

# Install development tools for code quality
py -m pip install -r requirements-dev.txt
```

### 2. Configure Development Environment

#### Option A: VS Code (Recommended)
```powershell
# Install recommended extensions
code --install-extension ms-python.python
code --install-extension ms-python.flake8
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort

# Open project
code .
```
VS Code will automatically:
- Format code on save with Black
- Sort imports with isort
- Show linting errors with flake8
- Run tests in the sidebar

#### Option B: Manual Setup
```powershell
# Enable pre-commit hooks (optional but recommended)
py -m pre_commit install

# This will run quality checks automatically before each commit
```

### 3. Verify Setup
```powershell
# Run all quality checks
py scripts\quality_check.py

# Should output:
# ✅ All quality checks passed!
# 🎉 Ready to commit!
```

## Development Workflow

### Daily Development
1. **Code**: VS Code auto-formats on save
2. **Before commit**: Run `py scripts\quality_check.py`
3. **Fix issues**: Run `scripts\fix_quality.bat` if needed
4. **Test**: All tests pass before committing

### Quality Commands Reference
```powershell
# Quick fix common issues
scripts\fix_quality.bat

# Individual quality checks
py -m flake8 src/                  # Linting
py -m black --check src/           # Format check
py -m black src/                   # Auto-format
py -m isort --check-only src/      # Import check
py -m isort src/                   # Fix imports
py -m mypy src/                    # Type checking
py -m bandit -r src/               # Security scan

# Testing
py -m pytest tests/unit/           # Fast unit tests (0.69s)
py -m pytest tests/integration/    # Integration tests (~30s)
py -m pytest tests/ui/             # Browser tests (requires Chrome)
```

## Project Structure
```
GameExperiment/
├── src/                    # Source code
│   ├── game/              # Game logic (business layer)
│   └── web/               # Web layer (Flask/SocketIO)
├── tests/                 # Test suite
│   ├── unit/              # Fast unit tests
│   ├── integration/       # Integration tests
│   └── ui/                # Browser-based UI tests
├── scripts/               # Development scripts
├── templates/             # HTML templates
├── static/                # CSS/JS/assets
└── deployment/            # Production deployment files
```

## Code Quality Standards

### What's Automatically Enforced
- **PEP8 compliance** (flake8)
- **Consistent formatting** (Black, 120 char lines)
- **Organized imports** (isort)
- **Input validation** on all socket handlers
- **Type hints** for new functions
- **Security checks** (bandit)
- **Test coverage** (64 unit + 9 integration tests)

### Manual Review Guidelines
See `CODE_REVIEW_CHECKLIST.md` for detailed review criteria.

## Getting Help

### Common Issues
1. **Quality checks fail**: Run `scripts\fix_quality.bat`
2. **Tests fail**: Check if server is already running on port 5000
3. **Import errors**: Ensure you're in the project root directory
4. **VS Code not formatting**: Check that extensions are installed

### Resources
- `.copilot-instructions.md` - Development context and patterns
- `CODE_REVIEW_CHECKLIST.md` - Manual review guidelines
- `deployment/DEPLOYMENT_STATUS.md` - Production deployment info

### Contact
- Check existing issues and documentation first
- Follow the established code quality standards
- Write tests for new features
