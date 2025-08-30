# Deployment script for Bribery Game Vue.js frontend

Write-Host "Starting Vue.js frontend deployment..." -ForegroundColor Cyan

# Navigate to the project directory
Set-Location $PSScriptRoot
Set-Location vue-bribery

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
npm ci

# Build for production
Write-Host "Building for production..." -ForegroundColor Cyan
npm run build

# Verify build
if (-not (Test-Path -Path "../static/vue")) {
    Write-Host "Build failed: output directory not found" -ForegroundColor Red
    exit 1
}

Write-Host "Checking for Flask integration..." -ForegroundColor Cyan

# Check if the Flask template exists
if (-not (Test-Path -Path "../templates/vue_app.html")) {
    Write-Host "Warning: Flask template for Vue app not found" -ForegroundColor Yellow
}

Write-Host "Vue.js frontend deployment completed successfully!" -ForegroundColor Green
Write-Host "Access the new Vue.js frontend at /vue" -ForegroundColor Green
