# Docker Implementation for Bribery Game

This directory contains the Docker implementation for the Bribery Game project.

## Files Overview

- `Dockerfile` - Defines the container image for the application
- `docker-compose.yml` - Defines the service configuration for local development
- `docker-helper.ps1` - PowerShell script with helpful Docker commands
- `build-docker.ps1` - PowerShell script for testing Docker builds locally
- `.dockerignore` - Specifies files to exclude from the Docker build
- `requirements-docker.txt` - Docker-specific dependencies for reliable builds
- `.github/workflows/docker-deploy.yml` - GitHub Actions workflow for Docker deployment
- `.github/workflows/docker-diagnostic.yml` - Diagnostic workflow for troubleshooting Docker builds
- `deployment/DOCKER_DEPLOYMENT.md` - Documentation for Docker deployment
- `deployment/install-docker-oracle.sh` - Script to install Docker on Oracle Cloud

## Getting Started with Docker

### Local Development

1. **Start the application**:
   ```powershell
   .\docker-helper.ps1 start
   ```

2. **View logs**:
   ```powershell
   .\docker-helper.ps1 logs
   ```

3. **Stop the application**:
   ```powershell
   .\docker-helper.ps1 stop
   ```

4. **Test Docker builds locally**:
   ```powershell
   # Build and test without running
   .\build-docker.ps1 -Test
   
   # Build and run the container
   .\build-docker.ps1 -Run
   
   # Clean build (no cache)
   .\build-docker.ps1 -NoBuildCache
   ```

### Deploying to Oracle Cloud

1. **Set up GitHub Secrets**:
   - `ORACLE_HOST_IP` - Oracle Cloud instance IP
   - `ORACLE_USERNAME` - SSH username (usually 'ubuntu')
   - `ORACLE_SSH_PRIVATE_KEY` - Private SSH key for Oracle Cloud
   - `GH_PAT` - GitHub Personal Access Token with repository scope

2. **Install Docker on Oracle Cloud**:
   - Run the GitHub Actions workflow `Setup Docker Environment`
   - Or manually run the `deployment/install-docker-oracle.sh` script on your Oracle Cloud instance

3. **Deploy the application**:
   - Push to the `master` branch to trigger automatic deployment
   - Or manually build and push the Docker image

## Advantages of Docker Deployment

- **Consistent Environments** - Eliminates "works on my machine" issues
- **Simplified Deployment** - No more Python version or venv issues
- **Faster Setup** - Quick environment provisioning with Docker
- **Easier Updates** - Simple to update and rollback with container images

## Commands Reference

See the `docker-helper.ps1` script for a full list of helpful commands:

```powershell
.\docker-helper.ps1 help
```
