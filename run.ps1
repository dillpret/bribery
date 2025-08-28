# PowerShell script to run the Bribery Game
Write-Host "Checking for virtual environment..." -ForegroundColor Cyan

# Check for venv in common locations
$venvPaths = @("venv", ".venv", "env")
$venvActivated = $false

foreach ($path in $venvPaths) {
    $activateScript = Join-Path -Path $path -ChildPath "Scripts\Activate.ps1"
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

# Run the application
py app.py

# This line will only execute if the server is stopped
Write-Host "`nServer stopped. Press any key to exit..." -ForegroundColor Yellow
$host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") | Out-Null
