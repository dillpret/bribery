# Docker Deployment for Bribery Game

This document describes how to deploy the Bribery Game using Docker, both locally and on Oracle Cloud.

## Prerequisites

- Docker installed on your local machine for development
- Docker installed on your Oracle Cloud instance for production

## Local Development with Docker

### Quick Start

```powershell
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Testing the Docker Build

```powershell
# Build the Docker image
docker build -t bribery-game .

# Run the container
docker run -p 5000:5000 bribery-game

# Access the application at http://localhost:5000
```

## Manual Deployment to Oracle Cloud

If you need to deploy manually without GitHub Actions:

1. **Build the Docker image locally**:
   ```powershell
   docker build -t bribery-game .
   ```

2. **Tag the image for your registry**:
   ```powershell
   docker tag bribery-game ghcr.io/yourusername/bribery:latest
   ```

3. **Push to the registry**:
   ```powershell
   docker push ghcr.io/yourusername/bribery:latest
   ```

4. **SSH into your Oracle Cloud instance**:
   ```powershell
   ssh -i path/to/key.pem ubuntu@your-oracle-ip
   ```

5. **Pull and run the container**:
   ```bash
   docker pull ghcr.io/yourusername/bribery:latest
   docker stop bribery-game || true
   docker rm bribery-game || true
   docker run -d --name bribery-game -p 80:5000 --restart unless-stopped ghcr.io/yourusername/bribery:latest
   ```

## Automated Deployment with GitHub Actions

The repository is configured with GitHub Actions for automated testing and deployment:

1. Every push to the `master` branch triggers the workflow
2. Tests are run on Windows to ensure compatibility
3. If tests pass, a Docker image is built and pushed to GitHub Container Registry
4. The image is deployed to Oracle Cloud via SSH
5. Nginx is automatically configured as a reverse proxy to forward requests from port 80 to the application

### Nginx Reverse Proxy Configuration

The deployment automatically:
1. Installs Nginx if not already present
2. Runs the Docker container on port 8080 (internal)
3. Configures Nginx to proxy requests from port 80 to port 8080
4. Enables WebSocket support for SocketIO
5. Removes any default Nginx sites that might conflict
6. Reloads Nginx to apply the changes

### Setting Up GitHub Actions Secrets

You need to configure the following secrets in your GitHub repository:

- `ORACLE_HOST_IP`: The IP address of your Oracle Cloud instance
- `ORACLE_USERNAME`: The SSH username (usually 'ubuntu')
- `ORACLE_SSH_PRIVATE_KEY`: The private SSH key to access your Oracle Cloud instance
- `GH_PAT`: GitHub Personal Access Token with repository scope for container registry access

## Troubleshooting

### Docker Image Issues

If the Docker image fails to build:

```powershell
# Build with verbose output
docker build --no-cache -t bribery-game .
```

### Container Runtime Issues

If the container fails to start:

```powershell
# Run with interactive console
docker run -it -p 5000:5000 bribery-game /bin/bash

# Check logs of a running container
docker logs bribery-game
```

### Oracle Cloud Deployment Issues

If deployment to Oracle Cloud fails:

1. Ensure Docker is installed on your Oracle Cloud instance
2. Check that your SSH key has the correct permissions
3. Verify that port 80 is open in your Oracle Cloud security list
4. Check the container logs: `docker logs bribery-game`

### Port Conflicts

If you encounter "address already in use" errors:

```bash
# Check what's using port 80
sudo lsof -i :80
# or
sudo ss -tulpn | grep :80

# The automatic deployment will configure Nginx as a reverse proxy
# If you need to debug Nginx configuration:
sudo nginx -t
sudo systemctl status nginx
sudo cat /etc/nginx/sites-available/bribery-game
```

The current deployment uses Nginx as a reverse proxy, so the Docker container runs on port 8080 internally while Nginx handles external requests on port 80. This setup helps avoid port conflicts with other services.

## Caching and Version Management

The application uses versioned static URLs to prevent browser caching issues. When deploying a new version:

1. Ensure the `VERSION` file has been updated (happens automatically with Git commits)
2. Rebuild and redeploy the Docker container
3. Browser clients should automatically receive the new version of all static assets

If you're still experiencing caching issues after deployment:

1. Verify Nginx isn't adding its own caching headers that override the application's settings
2. Check that your CDN (if using one) isn't aggressively caching static assets
3. Consider adding a version-specific route to Nginx for critical static assets

See `docs/VERSION_MANAGEMENT.md` for more details on the versioning and cache busting system.
