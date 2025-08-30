#!/bin/bash

# ShopEAT Setup Script with UV Package Manager
# This script helps you set up the development environment using UV

set -e

echo "🚀 Welcome to ShopEAT Setup with UV!"
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Check if UV is installed, install if not
if ! command -v uv &> /dev/null; then
    echo "📦 Installing UV package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.cargo/env  # Reload shell environment
    echo "✅ UV installed successfully"
else
    echo "✅ UV is already installed"
fi

# Setup backend with UV
echo "🐍 Setting up Python backend with UV..."
cd backend

# Create virtual environment with UV
if [ ! -d ".venv" ]; then
    uv venv
    echo "✅ Created Python virtual environment with UV"
else
    echo "✅ Python virtual environment already exists"
fi

# Activate virtual environment and install dependencies
source .venv/bin/activate
uv pip install -e .
echo "✅ Backend dependencies installed with UV"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Created .env file (please edit with your OpenAI API key)"
else
    echo "✅ .env file already exists"
fi

cd ..

# Setup frontend
echo "🟨 Setting up JavaScript frontend..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file already exists"
fi

cd ..

echo ""
echo "🎉 Setup complete with UV!"
echo "=========================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Start the backend: cd backend && source .venv/bin/activate && python main.py"
echo "3. Start the frontend: cd frontend && npm start"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "UV Commands:"
echo "- Install dev dependencies: cd backend && uv pip install -e '.[dev]'"
echo "- Add new package: cd backend && uv add package-name"
echo "- Run tests: cd backend && uv run pytest"
echo "- Format code: cd backend && uv run black ."
echo "- Lint code: cd backend && uv run flake8 ."
echo ""
echo "Or use Docker: docker-compose up --build"
echo ""
echo "Happy shopping with UV! 🛒🎤"
