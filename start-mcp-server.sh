#!/bin/bash

# Start MCP Server Script
# This script starts the FastAPI MCP server for the MedAI system

echo "🚀 Starting MedAI MCP Server..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/fastapi_mcp_server.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Change to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if port 8001 is available
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8001 is already in use. Stopping existing process..."
    lsof -ti:8001 | xargs kill -9
fi

# Start the MCP server
echo "🌐 Starting MCP server on http://localhost:8001"
echo "📚 API Documentation: http://localhost:8001/docs"
echo "🔍 MCP Tools: http://localhost:8001/mcp/tools"
echo "💚 Health Check: http://localhost:8001/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python fastapi_mcp_server.py