#!/bin/bash
# GitHub Actions simplified update script for Bribery Game
# This script avoids using virtual environments and uses system Python

set -e  # Exit on error

echo "🚀 Starting GitHub Actions simplified deployment update..."

# Create app directory if it doesn't exist
echo "📁 Checking application directory..."
if [ ! -d "/var/www/bribery-game" ]; then
    echo "Creating application directory..."
    sudo mkdir -p /var/www/bribery-game
    sudo chown $USER:$USER /var/www/bribery-game
fi

# Install required packages if not already installed
echo "📦 Checking system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-dev nginx git

# Copy application files (preserving structure)
echo "📋 Copying application files..."
rsync -av --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' --exclude='.git' --exclude='.github' ./ /var/www/bribery-game/
cd /var/www/bribery-game

# Install Python packages system-wide
echo "📦 Installing dependencies system-wide..."
sudo -H pip3 install --upgrade pip
sudo -H pip3 install -r requirements.txt
sudo -H pip3 install gunicorn eventlet

# Create a simple start script if it doesn't exist
if [ ! -f "start.sh" ]; then
    echo "📝 Creating startup script..."
    cat > start.sh << 'EOF'
#!/bin/bash
cd /var/www/bribery-game
python3 -m gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 deployment.wsgi:app
EOF
    chmod +x start.sh
fi

# Check if service file exists and update if needed
SERVICE_FILE="/etc/systemd/system/bribery-game.service"
if [ ! -f "$SERVICE_FILE" ]; then
    echo "🔧 Creating systemd service file..."
    sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Bribery Game Flask App
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/bribery-game
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="FLASK_ENV=production"
Environment="PORT=5000"
ExecStart=/var/www/bribery-game/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
EOF
fi

# Configure Nginx if needed
NGINX_FILE="/etc/nginx/sites-available/bribery-game"
if [ ! -f "$NGINX_FILE" ]; then
    echo "🌐 Setting up Nginx..."
    sudo bash -c "cat > $NGINX_FILE" << EOF
server {
    listen 80;
    server_name _;
    
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
    }
}
EOF

    # Enable the Nginx site if not already enabled
    if [ ! -f "/etc/nginx/sites-enabled/bribery-game" ]; then
        sudo ln -s /etc/nginx/sites-available/bribery-game /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
    fi
fi

# Apply changes and restart services
echo "🚀 Restarting services..."
sudo systemctl daemon-reload
sudo systemctl enable bribery-game
sudo systemctl restart bribery-game
sudo systemctl reload nginx

echo "✅ Deployment update complete!"
echo "📊 Service status:"
sudo systemctl status bribery-game --no-pager

# Show process information
echo "🔍 Process check:"
ps aux | grep python | grep -v grep

# Show listening ports
echo "🌐 Port check:"
sudo netstat -tuln | grep 5000 || echo "Service not listening on port 5000 yet"
