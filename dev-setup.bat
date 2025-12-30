@echo off
REM Quick setup script for local development (Windows)

setlocal enabledelayedexpansion

echo.
echo ================================
echo 🚀 FleetFlow Dev Setup
echo ================================
echo.

REM Check if Docker is running
echo 1️⃣  Checking Docker...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    exit /b 1
)
echo ✅ Docker is running
echo.

REM Start infrastructure
echo 2️⃣  Starting infrastructure (PostgreSQL + RabbitMQ)...
docker-compose up -d
echo ✅ Infrastructure started
echo    PostgreSQL:  localhost:5432
echo    RabbitMQ:    localhost:5672
echo    RabbitMQ UI: http://localhost:15672
echo.

REM Create Python virtual environment
echo 3️⃣  Setting up Python environment...
cd backend

if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate and install dependencies
call venv\Scripts\activate.bat
pip install -r requirements.txt -q
echo ✅ Dependencies installed
echo.

cd ..

echo.
echo ================================
echo ✅ Setup Complete!
echo ================================
echo.
echo 📝 Next steps:
echo.
echo Terminal 1 - Run FastAPI:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python -m uvicorn src.main:app --reload
echo.
echo Terminal 2 - Run Worker:
echo   cd backend
echo   venv\Scripts\activate.bat
echo   python src/worker.py
echo.
echo Terminal 3 - Test handshake:
echo   pip install aiohttp
echo   python test_handshake.py
echo.
echo 📚 Swagger docs: http://localhost:8000/docs
echo 🎚️  RabbitMQ UI: http://localhost:15672 (guest/guest)
echo.
pause
