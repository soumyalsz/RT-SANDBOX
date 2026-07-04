# run.ps1
# This script runs the RT-SANDBOX main script.

$ErrorActionPreference = "Stop"

# Ensure virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate virtual environment and run the script
Write-Host "Running runner/main.py..." -ForegroundColor Cyan
$env:VIRTUAL_ENV = "$PWD\.venv"
$env:PATH = "$PWD\.venv\Scripts;$env:PATH"

python runner/main.py
