#!/bin/bash
# Oracle Cloud update script for GitHub Actions deployment
# This script is similar to deploy-oracle.sh but optimized for CI/CD updates

set -e  # Exit on error

echo "🚀 Starting GitHub Actions deployment update..."

# Create app directory if it doesn't exist
echo "📁 Checking application directory..."
if [ ! -d "/var/www/bribery-game" ]; then
    echo "Creating application directory..."
    sudo mkdir -p /var/www/bribery-game
    sudo chown $USER:$USER /var/www/bribery-game
fi

# Copy application files (preserving structure)
echo "📋 Copying application files..."
rsync -av --exclude='.venv' --exclude='__pycache__' --exclude='.pytest_cache' --exclude='*.pyc' --exclude='.git' --exclude='.github' ./ /var/www/bribery-game/
cd /var/www/bribery-game

# Create virtual environment if it doesn't exist
echo "🔧 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "Virtual environment doesn't exist, creating..."
    python3.11 -m venv venv
else
    echo "Virtual environment already exists, skipping creation..."
fi

source venv/bin/activate

# Upgrade pip and install dependencies
echo "📦 Upgrading pip and installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install additional production dependencies if not already present
if ! pip freeze | grep -q "gunicorn"; then
    echo "Installing production dependencies..."
    pip install gunicorn[eventlet]
else
    echo "Production dependencies already installed, skipping..."
fi

# Run the main deployment script for service setup and Nginx config
echo "⚙️ Running main deployment script..."
chmod +x deployment/deploy-oracle.sh
./deployment/deploy-oracle.sh

echo ""
echo "🎉 GitHub Actions deployment complete!"
