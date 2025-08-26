# Docker Helper for Bribery Game
# This script provides helpful commands for managing the Docker environment

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Docker Helper for Bribery Game" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Note: Docker container uses Python 3.11 for compatibility with all dependencies" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\docker-helper.ps1 [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  start       - Start the application with Docker Compose"
    Write-Host "  stop        - Stop the running containers"
    Write-Host "  restart     - Restart the application"
    Write-Host "  logs        - View application logs"
    Write-Host "  build       - Rebuild the Docker image"
    Write-Host "  test        - Run tests inside Docker"
    Write-Host "  shell       - Open a shell inside the running container"
    Write-Host "  clean       - Remove all containers and images"
    Write-Host "  help        - Show this help message"
    Write-Host ""
}

function Start-App {
    Write-Host "Starting Bribery Game..." -ForegroundColor Cyan
    docker-compose up -d
    Write-Host "Application is running at http://localhost:5000" -ForegroundColor Green
}

function Stop-App {
    Write-Host "Stopping Bribery Game..." -ForegroundColor Cyan
    docker-compose down
    Write-Host "Application stopped" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "Showing logs (press Ctrl+C to exit)..." -ForegroundColor Cyan
    docker-compose logs -f
}

function Rebuild-App {
    Write-Host "Rebuilding Docker image..." -ForegroundColor Cyan
    docker-compose build --no-cache
    Write-Host "Build complete" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "Running tests inside Docker..." -ForegroundColor Cyan
    docker-compose run --rm bribery-game python -m pytest tests/unit/ -v
}

function Open-Shell {
    Write-Host "Opening shell inside container..." -ForegroundColor Cyan
    docker-compose exec bribery-game /bin/bash
}

function Clean-Environment {
    Write-Host "Removing all Docker containers and images for this project..." -ForegroundColor Cyan
    docker-compose down --rmi all --volumes --remove-orphans
    Write-Host "Clean complete" -ForegroundColor Green
}

function Restart-App {
    Write-Host "Restarting Bribery Game..." -ForegroundColor Cyan
    docker-compose restart
    Write-Host "Application restarted" -ForegroundColor Green
}

# Execute the requested command
switch ($Command) {
    "start" { Start-App }
    "stop" { Stop-App }
    "logs" { Show-Logs }
    "build" { Rebuild-App }
    "test" { Run-Tests }
    "shell" { Open-Shell }
    "clean" { Clean-Environment }
    "restart" { Restart-App }
    default { Show-Help }
}
