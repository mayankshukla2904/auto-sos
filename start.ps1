# Emergency Alert System - Windows Startup Script
# This script starts both the WhatsApp service and wake word detector

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Emergency Alert System - Starting Services" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
Write-Host "[1/4] Checking Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node --version
    Write-Host "      Node.js installed: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "      Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
Write-Host "[2/4] Checking Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "      Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "      ERROR: Python not found!" -ForegroundColor Red
    Write-Host "      Please install Python from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check if dependencies are installed
Write-Host "[3/4] Checking dependencies..." -ForegroundColor Yellow

if (-Not (Test-Path "node_modules")) {
    Write-Host "      Node modules not found. Installing..." -ForegroundColor Yellow
    npm install
}

# Check Python packages
$pipList = pip list 2>&1
if ($pipList -notmatch "pyaudio") {
    Write-Host "      Python packages not found. Installing..." -ForegroundColor Yellow
    Write-Host "      (This may take a few minutes)" -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host "      Dependencies OK" -ForegroundColor Green

# Check configuration
Write-Host "[4/4] Checking configuration..." -ForegroundColor Yellow
if (-Not (Test-Path "config.json")) {
    Write-Host "      ERROR: config.json not found!" -ForegroundColor Red
    Write-Host "      Please create config.json from the README" -ForegroundColor Red
    exit 1
}

$config = Get-Content "config.json" | ConvertFrom-Json
if ($config.whatsapp.recipient -eq "1234567890@s.whatsapp.net") {
    Write-Host ""
    Write-Host "      WARNING: You haven't configured the WhatsApp recipient!" -ForegroundColor Yellow
    Write-Host "      Edit config.json and set the correct phone number" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "      Press Enter to continue anyway, or Ctrl+C to exit..." -ForegroundColor Yellow
    Read-Host
}

Write-Host "      Configuration OK" -ForegroundColor Green
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting Services" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# Start WhatsApp service in a new window
Write-Host "Starting WhatsApp service..." -ForegroundColor Yellow
$whatsappProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "node whatsapp_service.js" -PassThru
Start-Sleep -Seconds 2

# Start wake word detector in a new window  
Write-Host "Starting wake word detector..." -ForegroundColor Yellow
$detectorProcess = Start-Process powershell -ArgumentList "-NoExit", "-Command", "python wake_word_detector_vosk.py" -PassThru

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   Services Started!" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Two windows have opened:" -ForegroundColor White
Write-Host "  1. WhatsApp Service (scan QR code if first run)" -ForegroundColor White
Write-Host "  2. Wake Word Detector (listening for 'help')" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Close both windows or press Ctrl+C in each" -ForegroundColor White
Write-Host ""
Write-Host "Testing wake word: Say 'help' clearly into your microphone" -ForegroundColor Cyan
Write-Host ""
