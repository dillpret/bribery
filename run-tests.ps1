# Test helper script for running unit tests with the correct dependencies

param(
    [switch]$UpdateDeps,
    [string]$TestPath = "tests/unit/",
    [string]$PythonVersion = "3"  # Default to 'py -3' but can be '3.11', etc.
)

Write-Host "Running unit tests for Bribery Game..." -ForegroundColor Cyan

# Use the specified Python version
$PyCmd = "py -$PythonVersion"
Write-Host "Using Python command: $PyCmd" -ForegroundColor Cyan

# Show Python version
Write-Host "Python version: " -ForegroundColor Yellow -NoNewline
Invoke-Expression "$PyCmd --version"

# Install dependencies if requested or if packages might be missing
if ($UpdateDeps) {
    Write-Host "Installing test dependencies..." -ForegroundColor Yellow
    Invoke-Expression "$PyCmd -m pip install --upgrade pip"
    Invoke-Expression "$PyCmd -m pip install -r requirements-test.txt"
    Invoke-Expression "$PyCmd -m pip install -r requirements-dev.txt"
}

# Run the tests
Write-Host "Running tests from: $TestPath" -ForegroundColor Yellow
Invoke-Expression "$PyCmd -m pytest $TestPath -v"
