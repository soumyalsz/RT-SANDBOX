# setup.ps1
# This script sets up the Python virtual environment and installs dependencies.

$ErrorActionPreference = "Stop"

Write-Host "Setting up RT-SANDBOX environment..." -ForegroundColor Cyan

# Check if .venv exists, if not, create it
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
$env:VIRTUAL_ENV = "$PWD\.venv"
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "requirements.txt not found!" -ForegroundColor Red
}
