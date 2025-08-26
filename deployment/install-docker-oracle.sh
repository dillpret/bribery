#!/bin/bash
# Oracle Cloud Docker installation and setup script

set -e  # Exit on error

echo "🐳 Installing Docker on Oracle Cloud..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker dependencies
echo "📦 Installing Docker dependencies..."
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
echo "🔑 Adding Docker's GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Add Docker repository
echo "📦 Adding Docker repository..."
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package database with Docker packages
echo "📦 Updating package database..."
sudo apt update

# Install Docker
echo "🐳 Installing Docker..."
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add current user to the docker group
echo "👤 Adding current user to the docker group..."
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Enable Docker to start on boot
echo "🚀 Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Configure Nginx as a reverse proxy
echo "🔄 Setting up Nginx as a reverse proxy..."
sudo apt install -y nginx

# Create Nginx configuration
sudo bash -c "cat > /etc/nginx/sites-available/bribery-game" << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/bribery-game /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "✅ Testing Nginx configuration..."
sudo nginx -t

# Restart Nginx
echo "🔄 Restarting Nginx..."
sudo systemctl restart nginx

echo ""
echo "🎉 Docker installation complete!"
echo "⚠️  You will need to log out and log back in for the Docker group changes to take effect."
echo "📝 To verify Docker installation, run: docker --version"
echo "🔄 To pull and run the Bribery Game, run: docker pull ghcr.io/YOUR_REPO/bribery:latest"
