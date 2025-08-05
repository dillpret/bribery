#!/bin/bash
# Oracle Cloud deployment script for Bribery Game

set -e  # Exit on error

echo "🚀 Starting Oracle Cloud deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11 and dependencies..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip nginx git

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/bribery-game
sudo chown $USER:$USER /var/www/bribery-game

# Copy application files (preserving structure)
echo "📋 Copying application files..."
rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' ./ /var/www/bribery-game/
cd /var/www/bribery-game

# Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn[eventlet]

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
sudo tee /etc/systemd/system/bribery-game.service > /dev/null <<EOF
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

# Configure Nginx
sudo tee /etc/nginx/sites-available/bribery-game > /dev/null <<EOF
server {
    listen 80;
    server_name _;

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
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/bribery-game /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Open firewall ports
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Start services
echo "🔄 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable bribery-game
sudo systemctl start bribery-game
sudo systemctl enable nginx
sudo systemctl restart nginx

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
echo "🔧 Useful commands:"
echo "   Check logs: sudo journalctl -u bribery-game -f"
echo "   Restart: sudo systemctl restart bribery-game"
echo "   Status: sudo systemctl status bribery-game"
echo ""
echo "🧪 To run tests on the server:"
echo "   cd /var/www/bribery-game"
echo "   source venv/bin/activate"
echo "   python3 -m pytest tests/unit/ -v"
