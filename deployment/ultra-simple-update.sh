#!/bin/bash
# Ultra-simple GitHub Actions update script for Bribery Game
# Uses system Python with --break-system-packages

set -e  # Exit on error
set -x  # Print all commands for debugging

echo "🚀 Starting ultra-simple GitHub Actions update..."

# Update app directory
echo "📋 Copying application files..."
sudo mkdir -p /var/www/bribery-game
rsync -av --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' --exclude='.git' --exclude='.github' ./ /var/www/bribery-game/
cd /var/www/bribery-game

# Update dependencies with --break-system-packages
echo "📦 Installing/updating Python packages..."
sudo -H python3 -m pip install --upgrade pip --break-system-packages
sudo -H python3 -m pip install -r requirements.txt --break-system-packages
sudo -H python3 -m pip install gunicorn eventlet --break-system-packages

# Update the start script
echo "📝 Creating/updating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash
cd /var/www/bribery-game
python3 -m gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 deployment.wsgi:app
EOF
chmod +x start.sh

# Create/update systemd service
echo "🔧 Updating systemd service..."
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

# Restart services
echo "🚀 Restarting services..."
sudo systemctl daemon-reload
sudo systemctl restart bribery-game
sudo systemctl reload nginx

echo "✅ Update complete!"
echo "📊 Service status:"
sudo systemctl status bribery-game --no-pager
echo ""
echo "Testing application response:"
curl -s http://localhost:5000 | head -10
echo ""
