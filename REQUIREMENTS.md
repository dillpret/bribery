# Requirements Structure

This project uses multiple requirements files to organize dependencies:

## Primary Requirements Files

- `requirements.txt` - Core production dependencies for running the application
- `requirements-dev.txt` - Development dependencies (linting, formatting, etc.)
- `requirements-docker.txt` - Docker-specific build dependencies
- `requirements-test.txt` - Testing-specific dependencies

## Purpose of this Structure

### Why Multiple Requirements Files?

Different environments have different needs:

1. **Production** - Needs minimal dependencies to run efficiently
2. **Development** - Needs additional tools for code quality
3. **Docker** - Needs specific build tools and packages
4. **Testing** - Needs testing libraries and may need to avoid problematic packages

### Installation Instructions

For **local development**:
```
py -m pip install -r requirements.txt -r requirements-dev.txt
```

For **testing only**:
```
py -m pip install -r requirements-test.txt
```

For **Docker builds**:
```
pip install -r requirements-docker.txt
```

## Environment-Specific Configurations

### Production (Docker)
- Uses Python 3.11 to ensure full compatibility with all dependencies
- Includes both eventlet and gevent for optimal performance
- Dockerfile is explicitly pinned to Python 3.11

### Testing
- Can run on Python 3.11-3.13
- Uses eventlet only (no gevent) for better compatibility
- Relies on requirements-test.txt which excludes gevent

### Development
- Recommended to use Python 3.11 for full compatibility
- If using Python 3.13, may need to exclude gevent

## Known Issues

- **gevent** - Has compatibility issues with Python 3.13+ due to Cython compilation errors with the `long` type.
  - Solution: Production Docker uses Python 3.11
  - Testing uses eventlet without gevent
- **netifaces** - Requires C compilation; explicitly added to requirements-docker.txt with build dependencies to ensure proper installation.
