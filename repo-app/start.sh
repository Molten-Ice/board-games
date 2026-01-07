#!/bin/bash

echo "🍽️  Starting Foody Menu App..."
echo ""

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "❌ Tesseract OCR is not installed!"
    echo "Please install it first:"
    echo "  macOS: brew install tesseract"
    echo "  Ubuntu: sudo apt-get install tesseract-ocr"
    echo "  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    exit 1
fi

echo "✅ Tesseract OCR found"
echo ""

# Start backend
echo "🚀 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Start backend in background
python app.py &
BACKEND_PID=$!
echo "✅ Backend running on http://localhost:5000 (PID: $BACKEND_PID)"
echo ""

# Start frontend
cd ../frontend

echo "🚀 Starting frontend server..."

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Start frontend
echo "✅ Frontend starting on http://localhost:3000"
echo ""
echo "🎉 Foody Menu App is ready!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"

npm start

# Cleanup on exit
kill $BACKEND_PID
