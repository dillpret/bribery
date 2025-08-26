# Obsolete Deployment Scripts

This directory contains the legacy deployment scripts that have been replaced by the Docker-based deployment approach.

These scripts are kept for reference purposes only and should not be used for new deployments.

The recommended deployment approach is now Docker-based, as described in `../DOCKER_DEPLOYMENT.md`.

## List of Obsolete Scripts

- `deploy-oracle.sh`: Original Oracle Cloud deployment script
- `github-actions-update.sh`: Original GitHub Actions deployment script
- `simple-deploy-oracle.sh`: Simplified Oracle Cloud deployment script
- `simple-github-actions-update.sh`: Simplified GitHub Actions deployment script
- `ultra-simple-deploy.sh`: Ultra-simplified deployment script using system Python
- `ultra-simple-update.sh`: Ultra-simplified update script
- `ORACLE_DEPLOYMENT.md`: Original Oracle Cloud deployment documentation

## Why These Scripts Are Obsolete

These scripts encountered various issues with Python virtual environment setup, version conflicts, and system dependencies. The Docker-based approach resolves these issues by providing a consistent, isolated environment for the application.
