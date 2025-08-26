#!/usr/bin/env pwsh
# Docker build helper script for local testing

param(
    [switch]$NoBuildCache,
    [switch]$NoCache,
    [switch]$Run,
    [switch]$Test
)

Write-Host "🐳 Building Docker image for Bribery Game..." -ForegroundColor Cyan

$buildArgs = @("build", "-t", "bribery-game:local", ".")

if ($NoBuildCache) {
    $buildArgs += "--no-cache"
}

if ($NoCache) {
    $buildArgs += "--build-arg" 
    $buildArgs += "BUILDKIT_INLINE_CACHE=1"
}

Write-Host "Running: docker $($buildArgs -join ' ')" -ForegroundColor Yellow
docker $buildArgs

if ($?) {
    Write-Host "✅ Docker image built successfully!" -ForegroundColor Green
    
    if ($Test) {
        Write-Host "🧪 Testing if the image works..." -ForegroundColor Cyan
        docker run --rm bribery-game:local python -c "import socket; print(f'Container is working! Host IP: {socket.gethostbyname(socket.gethostname())}')"
        
        Write-Host "📋 Installed packages:" -ForegroundColor Cyan
        docker run --rm bribery-game:local pip list
    }
    
    if ($Run) {
        Write-Host "🚀 Running the container..." -ForegroundColor Cyan
        docker run -p 5000:5000 --name bribery-game-local bribery-game:local
    }
} else {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
}
