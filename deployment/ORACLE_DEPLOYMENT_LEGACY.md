# ORACLE DEPLOYMENT (LEGACY METHOD)

> **NOTE**: This is the legacy deployment method. The recommended approach is to use Docker deployment as described in `DOCKER_DEPLOYMENT.md`.

This document describes the traditional (non-Docker) deployment method for the Bribery Game to Oracle Cloud.

## Pre-Deployment Checklist

Before deploying, ensure your local development environment works:

```powershell
# Test locally first (Windows PowerShell)
cd C:\path\to\your\GameExperiment

# Run quality checks (if dev tools installed)
py scripts\quality_check.py

# Run unit tests
py -m pytest tests/unit/ -v

# Test the application starts
py app.py
# Should show: "🚀 Starting Bribery game server on 0.0.0.0:5000"

# Test in browser at http://localhost:5000
```

## Step 1: Create Oracle Cloud Account
1. Go to [Oracle Cloud](https://www.oracle.com/cloud/free/)
2. Sign up for Always Free account
3. Complete verification (requires credit card but won't be charged)

## Step 2: Create VM Instance
1. In Oracle Cloud Console, go to **Compute > Instances**
2. Click **Create Instance**
3. Configure:
   - **Name**: `bribery-game-server`
   - **Image**: `Ubuntu 22.04 LTS` (x86_64)
   - **Shape**: `VM.Standard.E2.1.Micro` (Always Free eligible)
   - **Boot Volume**: 47GB (max for free tier)
4. **Add SSH Key**: 
   - Upload your public key OR
   - Generate new key pair (download private key!)
5. **VCN Settings**: Use default (creates new VCN)
6. Click **Create**

## Step 3: Configure Security Rules
1. Go to **Networking > Virtual Cloud Networks**
2. Click your VCN name
3. Click **Security Lists** > **Default Security List**
4. Click **Add Ingress Rules**:
   - **Source CIDR**: `0.0.0.0/0`
   - **Destination Port**: `80`
   - **Protocol**: TCP
5. Add another rule for HTTPS:
   - **Source CIDR**: `0.0.0.0/0`
   - **Destination Port**: `443`
   - **Protocol**: TCP
