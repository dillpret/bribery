#!/bin/bash
# Ultra-simple Oracle Cloud deployment script for Bribery Game
# Uses system Python with --break-system-packages

set -e  # Exit on error
set -x  # Print all commands for debugging

echo "🚀 Starting ultra-simple Oracle Cloud deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt install -y python3 python3-pip python3-dev nginx git curl

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/bribery-game
sudo chown $USER:$USER /var/www/bribery-game

# Copy application files
echo "📋 Copying application files..."
rsync -av --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' --exclude='.git' --exclude='.github' ./ /var/www/bribery-game/
cd /var/www/bribery-game

# Install dependencies with --break-system-packages
echo "📦 Installing Python packages..."
sudo -H python3 -m pip install --upgrade pip --break-system-packages
sudo -H python3 -m pip install -r requirements.txt --break-system-packages
sudo -H python3 -m pip install gunicorn eventlet --break-system-packages

# Create simple start script
echo "📝 Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
cd /var/www/bribery-game
python3 -m gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 deployment.wsgi:app
EOF
chmod +x start.sh

# Create systemd service
echo "🔧 Setting up systemd service..."
sudo bash -c "cat > /etc/systemd/system/bribery-game.service" << EOF
[Unit]
Description=Bribery Game Flask App
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/bribery-game
Environment="PYTHONPATH=/var/www/bribery-game"
Environment="FLASK_ENV=production"
Environment="PORT=5000"
ExecStart=/var/www/bribery-game/start.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Setting up Nginx..."
sudo bash -c "cat > /etc/nginx/sites-available/bribery-game" << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Root directory for static files
    root /var/www/bribery-game;
    
    # Try to serve static files directly
    location /static/ {
        alias /var/www/bribery-game/static/;
        expires 30d;
    }
    
    # Pass everything else to the Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable the Nginx site
sudo ln -sf /etc/nginx/sites-available/bribery-game /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# Start everything
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable bribery-game
sudo systemctl restart bribery-game
sudo systemctl reload nginx

echo "✅ Deployment complete!"
echo "📊 Service status:"
sudo systemctl status bribery-game --no-pager
echo ""
echo "Testing application response:"
curl -s http://localhost:5000 | head -20
echo ""
echo "🔍 Log access:"
echo "- View logs: sudo journalctl -u bribery-game -f"
echo "- View Nginx logs: sudo tail -f /var/log/nginx/error.log"
