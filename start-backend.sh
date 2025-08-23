#!/bin/bash

echo "Starting MedAI Backend..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
cd backend
pip install -r requirements.txt

# Check if Google API credentials exist
if [ ! -f "credentials.json" ]; then
    echo "Warning: Google API credentials.json not found. Gmail and Calendar integration will not work."
    echo "Please place your Google API credentials file in the backend directory."
fi

# Start the server
echo "Starting FastAPI server on http://localhost:8000..."
echo "Press Ctrl+C to stop the server"
echo ""

python main.py