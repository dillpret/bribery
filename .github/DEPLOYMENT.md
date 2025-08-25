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
2. Set up SSH access to your Oracle Cloud instance
3. Copy the repository files to your server
4. Run the deployment script (`deployment/deploy-oracle.sh`)

## Troubleshooting

If the deployment fails, check the following:

1. Verify your SSH key has access to the server
2. Ensure the `deploy-oracle.sh` script is executable
3. Check the GitHub Actions logs for specific error messages
