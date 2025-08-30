#!/bin/bash
# Deployment script for Bribery Game Vue.js frontend

# Stop on errors
set -e

echo "Starting Vue.js frontend deployment..."

# Navigate to the project directory
cd "$(dirname "$0")"
cd vue-bribery

# Install dependencies
echo "Installing dependencies..."
npm ci

# Build for production
echo "Building for production..."
npm run build

# Verify build
if [ ! -d "../static/vue" ]; then
  echo "Build failed: output directory not found"
  exit 1
fi

echo "Checking for Flask integration..."

# Check if the Flask template exists
if [ ! -f "../templates/vue_app.html" ]; then
  echo "Warning: Flask template for Vue app not found"
fi

echo "Vue.js frontend deployment completed successfully!"
echo "Access the new Vue.js frontend at /vue"
