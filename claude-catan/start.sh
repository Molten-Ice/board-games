#!/bin/bash

echo "========================================="
echo "  Settlers of Catan - Multiplayer Game"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed"
    echo "Please install pip"
    exit 1
fi

# Install dependencies if needed
echo "Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt || pip3 install -r requirements.txt
fi

echo ""
echo "Starting Catan server..."
echo ""
echo "Once the server starts, open your browser to:"
echo "  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 server.py
