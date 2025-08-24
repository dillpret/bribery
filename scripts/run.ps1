# PowerShell script to run the Bribery Game

$projectRoot = Split-Path -Parent $PSScriptRoot

# Set the working directory to the project root
Set-Location $projectRoot

Write-Host "Checking for virtual environment..." -ForegroundColor Cyan

# Check for venv in common locations
$venvPaths = @("venv", ".venv", "env")
$venvActivated = $false

foreach ($path in $venvPaths) {
    $activateScript = Join-Path -Path $projectRoot -ChildPath "$path\Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        Write-Host "Activating virtual environment ($path)..." -ForegroundColor Green
        & $activateScript
        $venvActivated = $true
        break
    }
}

if (-not $venvActivated) {
    Write-Host "No virtual environment found. Running with system Python..." -ForegroundColor Yellow
}

Write-Host "Installing dependencies..." -ForegroundColor Cyan
py -m pip install -r requirements.txt

Write-Host "`nStarting Bribery Game Server..." -ForegroundColor Green
Write-Host "`nOpen your browser and go to: http://localhost:5000" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor White

# Run Flask development server
py -m flask run
