#!/bin/bash
# Quick setup script for local development (macOS/Linux)

set -e  # Exit on error

echo "================================"
echo "🚀 FleetFlow Dev Setup"
echo "================================"
echo ""

# Check if Docker is running
echo "1️⃣  Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Start infrastructure
echo "2️⃣  Starting infrastructure (PostgreSQL + RabbitMQ)..."
docker-compose up -d
echo "✅ Infrastructure started"
echo "   PostgreSQL:  localhost:5432"
echo "   RabbitMQ:    localhost:5672"
echo "   RabbitMQ UI: http://localhost:15672"
echo ""

# Create Python virtual environment
echo "3️⃣  Setting up Python environment..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

cd ..

echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "Terminal 1 - Run FastAPI:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python -m uvicorn src.main:app --reload"
echo ""
echo "Terminal 2 - Run Worker:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python src/worker.py"
echo ""
echo "Terminal 3 - Test handshake:"
echo "  pip install aiohttp"
echo "  python test_handshake.py"
echo ""
echo "📚 Swagger docs: http://localhost:8000/docs"
echo "🎚️  RabbitMQ UI: http://localhost:15672 (guest/guest)"
echo ""
