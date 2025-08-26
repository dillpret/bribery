#!/bin/bash
# Oracle Cloud deployment script for Bribery Game

set -e  # Exit on error

echo "🚀 Starting Oracle Cloud deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python - First try with Python 3.11, with fallbacks
echo "🐍 Installing Python and dependencies..."

# Debug output for environment
echo "System information:"
lsb_release -a || cat /etc/os-release
echo "Architecture: $(uname -m)"

# First try to install Python 3.11 (preferred)
if ! command -v python3.11 &> /dev/null; then
    echo "Attempting to install Python 3.11..."
    sudo apt update
    sudo apt install -y software-properties-common
    
    # Try adding deadsnakes PPA (may fail on some Oracle Linux instances)
    if sudo add-apt-repository -y ppa:deadsnakes/ppa; then
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils
        
        # Verify installation
        if command -v python3.11 &> /dev/null; then
            echo "Python 3.11 installed successfully!"
            python3.11 --version
            PYTHON_CMD="python3.11"
        else
            echo "Python 3.11 installation failed, will try Python 3.10"
        fi
    else
        echo "Failed to add deadsnakes PPA (common on Oracle Linux), trying alternative approach"
    fi
else
    echo "Python 3.11 already installed"
    python3.11 --version
    PYTHON_CMD="python3.11"
fi

# If Python 3.11 install failed, try Python 3.10
if [ -z "$PYTHON_CMD" ] && ! command -v python3.10 &> /dev/null; then
    echo "Attempting to install Python 3.10..."
    sudo apt update
    sudo apt install -y python3.10 python3.10-venv python3.10-dev
    
    if command -v python3.10 &> /dev/null; then
        echo "Python 3.10 installed successfully!"
        python3.10 --version
        PYTHON_CMD="python3.10"
    else
        echo "Python 3.10 installation failed, will try system Python"
    fi
elif [ -z "$PYTHON_CMD" ] && command -v python3.10 &> /dev/null; then
    echo "Python 3.10 already installed"
    python3.10 --version
    PYTHON_CMD="python3.10"
fi

# Fallback to system Python if neither 3.11 nor 3.10 worked
if [ -z "$PYTHON_CMD" ]; then
    echo "Falling back to system Python..."
    sudo apt update
    sudo apt install -y python3 python3-venv python3-dev
    python3 --version
    PYTHON_CMD="python3"
fi

# Install pip and other essential packages
echo "Installing pip and other essential packages..."
sudo apt install -y python3-pip

# Ensure venv is installed
echo "Installing venv package for ${PYTHON_CMD}..."
sudo apt install -y python3-venv

echo "Python setup complete. Using: ${PYTHON_CMD} ($(${PYTHON_CMD} --version 2>&1))"

# Install nginx and git if not present
if ! command -v nginx &> /dev/null; then
    sudo apt install -y nginx
fi
if ! command -v git &> /dev/null; then
    sudo apt install -y git
fi

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/bribery-game
sudo chown $USER:$USER /var/www/bribery-game

# Copy application files (preserving structure)
echo "📋 Copying application files..."
rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' ./ /var/www/bribery-game/
cd /var/www/bribery-game

# Create virtual environment if it doesn't exist or recreate if requested
echo "🔧 Setting up Python virtual environment..."
RECREATE_VENV=${RECREATE_VENV:-0}  # Default to not recreate

if [ ! -d "venv" ] || [ "$RECREATE_VENV" -eq 1 ]; then
    if [ -d "venv" ] && [ "$RECREATE_VENV" -eq 1 ]; then
        echo "Recreating virtual environment as requested..."
        rm -rf venv
    else
        echo "Virtual environment doesn't exist, creating..."
    fi
    
    echo "Creating virtual environment with ${PYTHON_CMD}..."
    
    # First attempt using the module approach
    ${PYTHON_CMD} -m venv venv || {
        echo "Error creating venv with module approach, trying alternatives..."
        
        # Try installing venv packages specific to the Python version
        echo "Installing venv packages for ${PYTHON_CMD}..."
        PYTHON_VERSION=$(${PYTHON_CMD} --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1-2)
        sudo apt-get install -y python${PYTHON_VERSION}-venv || sudo apt-get install -y python3-venv
        
        # Try again with the module approach
        ${PYTHON_CMD} -m venv venv || {
            echo "Still failing with module approach, trying virtualenv..."
            
            # Try using virtualenv as a fallback
            echo "Installing virtualenv as a fallback..."
            sudo apt-get install -y python3-virtualenv
            virtualenv -p ${PYTHON_CMD} venv || {
                echo "All attempts to create virtual environment failed."
                echo "Creating a simple directory structure as a last resort..."
                mkdir -p venv/bin
                echo "#!/bin/bash" > venv/bin/activate
                echo "export PATH=$(dirname $(which ${PYTHON_CMD})):\$PATH" >> venv/bin/activate
                echo "Using system Python directly without a true virtual environment."
            }
        }
    }
else
    echo "Virtual environment already exists, skipping creation..."
fi

source venv/bin/activate

# Check if venv was created
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment directory not created!"
    echo "Directory listing:"
    ls -la
    echo "Python versions available:"
    compgen -c python | grep python || echo "No Python commands found"
    exit 1
fi

echo "Activating virtual environment (or fallback)..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Virtual environment activated successfully."
else
    echo "WARNING: Standard virtual environment activation script not found."
    echo "Using fallback approach..."
    export PATH=$PWD/venv/bin:$PATH
    if [ -z "$VIRTUAL_ENV" ]; then
        export VIRTUAL_ENV=$PWD/venv
    fi
fi

# Verify Python is working
echo "Python version in environment:"
python --version || ${PYTHON_CMD} --version

# Upgrade pip and install dependencies with fallbacks
echo "📦 Upgrading pip and installing dependencies..."
pip install --upgrade pip || python -m pip install --upgrade pip || ${PYTHON_CMD} -m pip install --upgrade pip || sudo apt install -y python3-pip

# Check if requirements have changed by creating a hash file
REQUIREMENTS_HASH_FILE="venv/.requirements-hash"
CURRENT_HASH=$(md5sum requirements.txt | awk '{ print $1 }')

# Function to install packages with fallbacks
install_packages() {
    echo "Installing packages: $@"
    pip install $@ || python -m pip install $@ || ${PYTHON_CMD} -m pip install $@ || {
        echo "ERROR: Failed to install packages with pip. Trying system package manager..."
        for pkg in $@; do
            sudo apt install -y python3-$(echo $pkg | tr '[:upper:]' '[:lower:]')
        done
    }
}

# Install requirements with fallbacks
if [ ! -f "$REQUIREMENTS_HASH_FILE" ] || [ "$(cat $REQUIREMENTS_HASH_FILE)" != "$CURRENT_HASH" ]; then
    echo "Requirements have changed or first installation, installing dependencies..."
    pip install -r requirements.txt || python -m pip install -r requirements.txt || ${PYTHON_CMD} -m pip install -r requirements.txt || {
        echo "ERROR: Failed to install from requirements.txt directly."
        echo "Trying to install key packages individually..."
        
        # Install core dependencies individually
        install_packages flask flask-socketio
    }
    echo "$CURRENT_HASH" > "$REQUIREMENTS_HASH_FILE"
else
    echo "Requirements unchanged, skipping dependency installation..."
fi

# Install additional production dependencies if not already present
if ! pip freeze | grep -q "gunicorn"; then
    echo "Installing production dependencies..."
    install_packages "gunicorn[eventlet]" eventlet
else
    echo "Production dependencies already installed, skipping..."
fi

# Verify critical packages are installed
echo "Verifying critical packages..."
python -c "import flask, flask_socketio" || {
    echo "ERROR: Critical packages verification failed. Attempting emergency installation..."
    sudo apt-get install -y python3-flask python3-flask-socketio
}

# Make sure prompts.txt exists and is readable
echo "📝 Checking prompts file..."
if [ ! -f "data/prompts.txt" ]; then
    echo "⚠️  data/prompts.txt not found, creating default..."
    mkdir -p data
    cat > data/prompts.txt << 'EOF'
Write a haiku about your target
Create a meme description about your target
Compose a short song verse about your target
Write a funny review of your target as if they were a restaurant
Describe your target as a superhero
EOF
fi

# Create systemd service
echo "⚙️  Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/bribery-game.service"
SERVICE_CONTENT=$(cat <<EOF
[Unit]
Description=Bribery Game Flask App
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/bribery-game
Environment="PATH=/var/www/bribery-game/venv/bin"
Environment="FLASK_ENV=production"
Environment="PORT=5000"
ExecStart=/var/www/bribery-game/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 deployment.wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF
)

# Check if service file exists and is different
if [ ! -f "$SERVICE_FILE" ] || [ "$(echo "$SERVICE_CONTENT" | md5sum)" != "$(cat $SERVICE_FILE | md5sum)" ]; then
    echo "Creating or updating systemd service file..."
    echo "$SERVICE_CONTENT" | sudo tee $SERVICE_FILE > /dev/null
    SERVICE_UPDATED=1
else
    echo "Systemd service file unchanged, skipping..."
    SERVICE_UPDATED=0
fi

# Configure Nginx
NGINX_FILE="/etc/nginx/sites-available/bribery-game"
NGINX_CONTENT=$(cat <<EOF
server {
    listen 80;
    server_name bribery.highsc.org;  # Replace with your actual domain
    
    # Simple Cloudflare support - trusts CF-Connecting-IP header
    real_ip_header CF-Connecting-IP;
    
    # Root directory for static files
    root /var/www/bribery-game;
    
    # Try to serve static files directly first
    location /static/ {
        alias /var/www/bribery-game/static/;
        expires 30d;
    }
    
    # Pass everything else to the Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_buffering off;
        
        # Try the URI itself, then as a file, then as a directory, then fall back to proxy
        try_files \$uri @proxy;
    }
    
    # Named location for the proxy pass
    location @proxy {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
)

# Check if nginx config exists and is different
if [ ! -f "$NGINX_FILE" ] || [ "$(echo "$NGINX_CONTENT" | md5sum)" != "$(cat $NGINX_FILE | md5sum)" ]; then
    echo "Creating or updating nginx config file..."
    echo "$NGINX_CONTENT" | sudo tee $NGINX_FILE > /dev/null
    NGINX_UPDATED=1
else
    echo "Nginx config file unchanged, skipping..."
    NGINX_UPDATED=0
fi

# Enable site
sudo ln -sf /etc/nginx/sites-available/bribery-game /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Open firewall ports if ufw is active
if command -v ufw &> /dev/null; then
    echo "Configuring firewall..."
    sudo ufw allow 22
    sudo ufw allow 80
    sudo ufw allow 443
    if ! sudo ufw status | grep -q "Status: active"; then
        sudo ufw --force enable
    fi
fi

# Reload/restart services as needed
echo "🔄 Managing services..."
sudo systemctl daemon-reload

if [ "$SERVICE_UPDATED" -eq 1 ] || ! systemctl is-active --quiet bribery-game; then
    echo "Enabling and (re)starting bribery-game service..."
    sudo systemctl enable bribery-game
    sudo systemctl restart bribery-game
else
    echo "bribery-game service already running with current config, not restarting..."
fi

if [ "$NGINX_UPDATED" -eq 1 ]; then
    echo "Restarting nginx service due to config changes..."
    sudo systemctl restart nginx
else
    echo "Reloading nginx configuration..."
    sudo systemctl reload nginx
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Service Status:"
sudo systemctl status bribery-game --no-pager -l
echo ""
echo "🌐 Your game should be accessible at:"
echo "   http://$(curl -s ifconfig.me)"
echo "   http://your-oracle-instance-ip"
echo ""
echo "☁️  If using Cloudflare with Flexible SSL:"
echo "   1. Create an A record pointing to your server IP"
echo "   2. Set SSL/TLS mode to 'Flexible' in Cloudflare dashboard"
echo "   3. Enable 'Always Use HTTPS' for secure connections"
echo "   4. Visit https://your-domain.com to access your game"
echo ""
echo "🔧 Useful commands:"
echo "   Check logs: sudo journalctl -u bribery-game -f"
echo "   Restart: sudo systemctl restart bribery-game"
echo "   Status: sudo systemctl status bribery-game"
echo ""
echo "🧪 To run tests on the server:"
echo "   cd /var/www/bribery-game"
echo "   source venv/bin/activate"
echo "   python3 -m pytest tests/unit/ -v"
