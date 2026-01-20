#!/bin/bash

# Setup script for AI Diary project

set -e

echo "🚀 Setting up AI Diary project..."

# Check if required tools are installed
echo "Checking prerequisites..."

command -v node >/dev/null 2>&1 || { echo "❌ Node.js is not installed. Please install Node.js 20+"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is not installed. Please install Python 3.11+"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install Docker"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is not installed. Please install Docker Compose"; exit 1; }

echo "✅ Prerequisites check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from example..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual credentials"
else
    echo ".env file already exists"
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Add your Firebase service-account.json to the project root"
echo "3. Run 'docker-compose up' to start the application"
echo "4. Visit http://localhost:5173 to access the frontend"
echo ""

