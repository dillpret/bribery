# Deployment Troubleshooting Guide

This document provides solutions to common deployment issues when deploying the Bribery Game to Oracle Cloud.

## Python Virtual Environment Issues (Exit Code 127)

If you encounter the error `Process completed with exit code 127` during deployment when setting up the Python virtual environment, or if the virtual environment setup consistently fails:

### Manual Deployment Steps

1. **Connect to your instance**:
   ```bash
   ssh -i /path/to/your/private-key ubuntu@YOUR_PUBLIC_IP
   ```

2. **Install Python manually**:
   ```bash
   sudo apt update
   sudo apt install -y software-properties-common
   sudo add-apt-repository -y ppa:deadsnakes/ppa
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
   ```

3. **Clone the repository (if needed)**:
   ```bash
   git clone YOUR_REPO_URL
   cd YOUR_REPO_DIRECTORY
   ```

4. **Create the virtual environment manually**:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install gunicorn[eventlet]
   ```

5. **Continue with the rest of the deployment script**:
   ```bash
   sudo cp deployment/bribery-game.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable bribery-game
   sudo systemctl start bribery-game
   ```

### Alternative Python Versions

If Python 3.11 installation fails:

```bash
# Try Python 3.10
sudo apt install -y python3.10 python3.10-venv python3.10-dev
python3.10 -m venv venv

# Or system Python
sudo apt install -y python3 python3-venv python3-dev
python3 -m venv venv
```

### Using virtualenv as a Fallback

If the standard venv module fails:

```bash
sudo apt install -y python3-virtualenv
virtualenv -p python3.11 venv  # or python3.10, or python3
```

### Ultra-Simple Deployment (Direct Solution)

For "externally-managed-environment" errors or when all other approaches fail, use the ultra-simple deployment script:

```bash
# Use the ultra-simple deployment script
chmod +x deployment/ultra-simple-deploy.sh
./deployment/ultra-simple-deploy.sh
```

This script:
- Uses `--break-system-packages` flag to override Python's externally managed environment restriction
- Bypasses virtual environment complexity entirely
- Installs packages directly to system Python
- Provides verbose logging for easier troubleshooting

## Nginx Configuration Issues

If you have issues with Nginx:

```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

## Service Not Starting

If the bribery-game service doesn't start:

```bash
# Check service status
sudo systemctl status bribery-game

# View service logs
sudo journalctl -u bribery-game -f

# Restart the service
sudo systemctl restart bribery-game
```

## Permissions Issues

If you encounter permission problems:

```bash
# Set correct ownership
sudo chown -R $USER:$USER /var/www/bribery-game

# Set correct permissions
sudo chmod -R 755 /var/www/bribery-game
```

## Firewall Issues

If you can't access the application:

```bash
# Check if the firewall is allowing traffic
sudo ufw status

# Allow HTTP traffic if needed
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Verify Application is Running

To verify the application is running correctly:

```bash
# Check if the application is listening on port 5000
sudo netstat -tuln | grep 5000

# Test the application locally
curl http://localhost:5000
```

## No Output from journalctl

If `sudo journalctl -u bribery-game -f` doesn't show any output:

```bash
# Check if the service exists
ls -la /etc/systemd/system/bribery-game.service

# Check if the service is enabled
systemctl is-enabled bribery-game

# Try manually starting the service and check for errors
sudo systemctl restart bribery-game
sudo systemctl status bribery-game

# Look for any Python processes running
ps aux | grep python

# Check system-wide logs
sudo journalctl -f
```

If the service isn't creating any log entries, it may not be properly defined or started. Try using the simple deployment script which creates a straightforward service definition.
