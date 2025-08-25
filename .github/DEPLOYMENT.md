# GitHub Actions Deployment

This repository is configured to automatically deploy to Oracle Cloud when changes are pushed to the master branch.

## Setting Up GitHub Secrets

Before the automatic deployment will work, you need to set up two required secrets in your GitHub repository:

1. **ORACLE_SSH_PRIVATE_KEY**: Your SSH private key that has access to the Oracle Cloud instance
2. **ORACLE_HOST_IP**: The public IP address of your Oracle Cloud instance

### How to Add Secrets to Your GitHub Repository

1. Go to your GitHub repository
2. Click on "Settings" (near the top of the page)
3. In the left sidebar, click on "Secrets and variables" → "Actions"
4. Click on "New repository secret"
5. Add the following secrets:

### ORACLE_SSH_PRIVATE_KEY

1. Locate your SSH private key file (often `id_rsa` or the file you downloaded from Oracle)
2. Copy the entire contents of the file, including the `-----BEGIN RSA PRIVATE KEY-----` and `-----END RSA PRIVATE KEY-----` lines
3. Create a new secret with the name `ORACLE_SSH_PRIVATE_KEY` and paste the contents

### ORACLE_HOST_IP

1. Create a new secret with the name `ORACLE_HOST_IP`
2. Enter the public IP address of your Oracle Cloud instance (e.g., `123.456.789.012`)

## Deployment Process

When you push changes to the master branch, GitHub Actions will:

1. Check out your code
2. Read the current version from the `VERSION` file
3. Automatically increment the patch version
4. Commit the updated version back to the repository
5. Create a git tag with the new version (e.g., v0.0.2)
6. Set up SSH access to your Oracle Cloud instance
7. Copy the repository files to your server
8. Run the deployment script (`deployment/github-actions-update.sh`)

## Version Management

The deployment process automatically increments the patch version with every deployment. For minor or major version updates:

```powershell
# Update minor version (0.1.0 -> 0.2.0)
py scripts\bump_version.py minor

# Update major version (1.0.0 -> 2.0.0) 
py scripts\bump_version.py major
```

See `.github/VERSION.md` for more details on version management.

## Troubleshooting

If the deployment fails, check the following:

1. Verify your SSH key has access to the server
2. Ensure the `github-actions-update.sh` script is executable
3. Check the GitHub Actions logs for specific error messages
