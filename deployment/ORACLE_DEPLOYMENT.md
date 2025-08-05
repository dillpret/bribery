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

## Step 4: Connect to Your Instance
```bash
# Use the public IP from your instance details
ssh -i /path/to/your/private-key ubuntu@YOUR_PUBLIC_IP
```

## Step 5: Deploy Your Application

### Option A: Clone from Git Repository
```bash
# Clone your repository
git clone YOUR_REPO_URL
cd YOUR_REPO_DIRECTORY

# Make deployment script executable and run it
chmod +x deployment/deploy-oracle.sh
./deployment/deploy-oracle.sh
```

### Option B: Upload Files Manually
```bash
# If uploading files manually (using scp, rsync, etc.)
# Ensure all files including src/, templates/, static/, tests/ are copied

# Navigate to your uploaded directory
cd /path/to/your/uploaded/files

# Make deployment script executable and run it
chmod +x deployment/deploy-oracle.sh
./deployment/deploy-oracle.sh
```

### Verify Deployment
```bash
# Check service status
sudo systemctl status bribery-game

# Check if the application is running
curl http://localhost:5000

# View logs
sudo journalctl -u bribery-game -f
```

## Step 6: Set Up Domain (Optional)
1. **Free Domain**: Use [Freenom](https://freenom.com) or [No-IP](https://www.noip.com)
2. **Point DNS** to your Oracle instance public IP
3. **SSL Certificate**: Use Let's Encrypt (see SSL setup below)

## SSL Setup (Optional but Recommended)
```bash
# Install Certbot
sudo apt install snapd
sudo snap install --classic certbot

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

## Monitoring & Maintenance
```bash
# Check application status
sudo systemctl status bribery-game

# View logs
sudo journalctl -u bribery-game -f

# Restart application
sudo systemctl restart bribery-game

# Update application
cd /var/www/bribery-game
git pull
sudo systemctl restart bribery-game
```

## Testing Your Deployment

### Run Tests on Server
```bash
# Connect to your server
ssh -i /path/to/your/private-key ubuntu@YOUR_PUBLIC_IP

# Navigate to application directory
cd /var/www/bribery-game

# Activate virtual environment
source venv/bin/activate

# Run unit tests (fastest, no dependencies)
python3 -m pytest tests/unit/ -v

# Run integration tests (requires server to be running)
python3 -m pytest tests/integration/ -v

# Note: UI tests require browser and are not suitable for server testing
```

### Application Structure on Server
```
/var/www/bribery-game/
├── src/                    # Core application code
│   ├── game/              # Game logic
│   └── web/               # Flask app and Socket.IO
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # API tests
│   ├── ui/               # Browser tests
│   └── helpers/          # Test utilities
├── deployment/           # Deployment files
├── prompts.txt          # Game prompts
├── requirements.txt     # Python dependencies
├── wsgi.py             # Production entry point
└── venv/               # Python virtual environment
```

## Troubleshooting

### If service won't start:
```bash
# Check detailed logs
sudo journalctl -u bribery-game --no-pager -l

# Check if all dependencies are installed
cd /var/www/bribery-game
source venv/bin/activate
pip list

# Test manually
python3 wsgi.py
```

### If website not accessible:
1. **Check Oracle Cloud Security Lists** (port 80/443 open)
2. **Check Ubuntu firewall**: `sudo ufw status`
3. **Check Nginx**: `sudo systemctl status nginx`
4. **Check application**: `sudo systemctl status bribery-game`
5. **Check if port 5000 is responding**: `curl http://localhost:5000`

### Import/Module Errors:
```bash
# Ensure all files were copied correctly
ls -la /var/www/bribery-game/src/

# Check Python path in wsgi.py
cd /var/www/bribery-game
source venv/bin/activate
python3 -c "import sys; print(sys.path)"
python3 -c "from src.web import create_app; print('Import successful')"
```

### Memory issues:
```bash
# Check memory usage
free -h
htop

# If memory is low, restart services
sudo systemctl restart bribery-game
sudo systemctl restart nginx
```

### File Permission Issues:
```bash
# Fix ownership
sudo chown -R $USER:www-data /var/www/bribery-game
sudo chmod -R 755 /var/www/bribery-game

# Make sure wsgi.py is executable
chmod +x /var/www/bribery-game/wsgi.py
```

## Cost Monitoring
- Oracle Always Free includes:
  - 2 AMD compute instances (1/8 OCPU, 1 GB RAM each)
  - 47 GB total Block Volume storage
  - 10 GB Object Storage
  - This is **permanently free** (not trial)

## Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /home/ubuntu/backup_$DATE.tar.gz /var/www/bribery-game
# Upload to Oracle Object Storage or download locally
```

## Performance Optimization
Your game should run fine on the free tier, but if needed:
- Enable gzip compression in Nginx
- Use Redis for session storage (install with `sudo apt install redis-server`)
- Monitor with `htop` and optimize accordingly
