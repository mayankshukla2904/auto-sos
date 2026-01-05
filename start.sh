#!/bin/bash
# Emergency Alert System - Linux/Raspberry Pi Startup Script

echo ""
echo "=========================================================="
echo "   Emergency Alert System - Starting Services"
echo "=========================================================="
echo ""

# Check if Node.js is installed
echo "[1/4] Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "      ✓ Node.js installed: $NODE_VERSION"
else
    echo "      ✗ ERROR: Node.js not found!"
    echo "      Install with: sudo apt-get install nodejs npm"
    exit 1
fi

# Check if Python is installed
echo "[2/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "      ✓ Python installed: $PYTHON_VERSION"
else
    echo "      ✗ ERROR: Python not found!"
    echo "      Install with: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Check dependencies
echo "[3/4] Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "      Installing Node modules..."
    npm install
fi

if ! python3 -c "import pyaudio" &> /dev/null; then
    echo "      Installing Python packages..."
    pip3 install -r requirements.txt
fi

echo "      ✓ Dependencies OK"

# Check configuration
echo "[4/4] Checking configuration..."
if [ ! -f "config.json" ]; then
    echo "      ✗ ERROR: config.json not found!"
    exit 1
fi

echo "      ✓ Configuration OK"
echo ""
echo "=========================================================="
echo "   Starting Services"
echo "=========================================================="
echo ""

# Start WhatsApp service in background
echo "Starting WhatsApp service..."
node whatsapp_service.js > whatsapp_service.log 2>&1 &
WHATSAPP_PID=$!
sleep 2

# Start wake word detector
echo "Starting wake word detector..."
echo ""
python3 wake_word_detector_vosk.py

# Cleanup on exit
kill $WHATSAPP_PID 2>/dev/null
