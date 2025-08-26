# Bribery Game

Flask-SocketIO multiplayer game where players submit creative bribes and vote on submissions.

## Quick Start

### Using Docker (Recommended)
```powershell
# Start the application with Docker
docker-compose up -d

# Access the application at http://localhost:5000
```

### Traditional Setup
```powershell
# Production setup
py -m pip install -r requirements.txt
py -m flask run

# Development setup (includes code quality tools)
py -m pip install -r requirements.txt -r requirements-dev.txt
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
py -m pytest                # Full suite (unit tests only)
py -m pytest tests/unit/    # Unit tests
```

## Deployment

### Docker Deployment (Recommended)
This repository uses GitHub Actions with Docker for automated deployment to Oracle Cloud.

- **Auto-deployment**: Push to the `master` branch to trigger the workflow
- **Process**: Tests → Build Docker image → Push to registry → Deploy to Oracle Cloud
- **Configuration**: Set up required secrets in GitHub repository settings
- **Documentation**: See `deployment/DOCKER_DEPLOYMENT.md` for detailed instructions

### Legacy Deployment
For the legacy non-Docker deployment method, see `deployment/ORACLE_DEPLOYMENT.md`.

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
