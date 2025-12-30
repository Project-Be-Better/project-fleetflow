# FleetFlow - Local Development Setup (Hybrid Approach)

## 🎯 Architecture

- **Infrastructure (Docker):** PostgreSQL + RabbitMQ
- **Code (Local):** FastAPI API + Python Worker + (future) React Frontend

This hybrid approach gives you:

- ⚡ **Instant feedback** - No Docker rebuild on file save
- 🐛 **Easy debugging** - Attach IDE debugger directly
- 🚀 **Fast iteration** - `uvicorn --reload` and `npm run dev`

---

## 📋 Prerequisites

- **Docker & Docker Compose** - For infrastructure
- **Python 3.11+** - For FastAPI and Worker
- **Node.js 18+** - For React frontend (coming soon)

---

## 🚀 Quick Start

### 1. Start Infrastructure (One-time)

```bash
# Start PostgreSQL and RabbitMQ in Docker
docker-compose up -d

# Verify services are healthy
docker-compose ps
```

Expected output:

```
CONTAINER ID   NAMES              STATUS
abc123...      fleetflow-db       Up (healthy)
def456...      fleetflow-mq       Up (healthy)
```

### 2. Set Up Python Environment

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run FastAPI (Terminal 1)

```bash
cd backend

# Make sure venv is activated
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Output:

```
Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
Watching for file changes...
```

✅ API is now running on **http://localhost:8000**
📚 Swagger docs: **http://localhost:8000/docs**

### 4. Run Worker (Terminal 2)

```bash
cd backend

# Make sure venv is activated
python src/worker.py
```

Output:

```
🚀 Worker listening on queue: telemetry_analysis
Press CTRL+C to stop
```

✅ Worker is now consuming messages

### 5. Test the Handshake (Terminal 3)

```bash
# Install test dependencies
pip install aiohttp

# Run the test
python test_handshake.py
```

Expected output:

```
============================================================
🚗 FleetFlow Vertical Slice Handshake Test
============================================================

1️⃣  Submitting telemetry...
✅ Accepted: trip_id = a1b2c3d4-e5f6-7890-abcd-ef1234567890

2️⃣  Waiting for worker to process (max 10s)...

3️⃣  Retrieving calculated score...
✅ Score retrieved (attempt 1):
   Safety Score: 90/100
   Harsh Braking Events: 1
   Rapid Acceleration Events: 1

============================================================
✅ HANDSHAKE SUCCESSFUL!
============================================================
```

---

## 🔧 Development Workflow

### Making Changes

1. **Edit code** in `backend/src/`
2. **FastAPI auto-reloads** (watch for `Reloading` message in Terminal 1)
3. **Test in VS Code** or with curl/Postman
4. **Worker picks up changes** automatically

### Debugging in VS Code

**Stop FastAPI** and run with debugger:

```bash
# Terminal 1
python -m debugpy --listen 5678 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**.vscode/launch.json** configuration:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Attach to FastAPI",
      "type": "python",
      "request": "attach",
      "port": 5678,
      "host": "127.0.0.1"
    }
  ]
}
```

Then press **F5** to attach debugger.

---

## 🧪 Manual Testing

### Submit Telemetry

```bash
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
    "driver_id": "c9284200-e29b-41d4-a716-446655440000",
    "timestamp": "2025-01-01T12:00:00Z",
    "data": [
      {"speed_kmh": 50, "g_force_long": 0.1, "g_force_lat": 0},
      {"speed_kmh": 55, "g_force_long": -0.5, "g_force_lat": 0}
    ]
  }'
```

Response:

```json
{
  "status": "QUEUED",
  "trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Retrieve Score (after ~1s)

```bash
curl http://localhost:8000/api/v1/trip/a1b2c3d4-e5f6-7890-abcd-ef1234567890/score
```

Response:

```json
{
  "trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "safety_score": 95,
  "harsh_braking_count": 1,
  "rapid_accel_count": 0,
  "created_at": "2025-01-01T12:00:01.000Z"
}
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🚦 Monitoring Infrastructure

### PostgreSQL

```bash
# Connect to database
psql postgresql://postgres:password@localhost:5432/fleetflow

# List tables
\dt telemetry.*

# View trip logs
SELECT id, vehicle_id, status FROM telemetry.trip_logs;

# View driver scores
SELECT trip_id, safety_score FROM telemetry.driver_scores;
```

### RabbitMQ Management UI

Open **http://localhost:15672** in browser

- Username: `guest`
- Password: `guest`

View:

- Active queues
- Message count
- Consumer status

### Container Logs

```bash
# PostgreSQL logs
docker logs -f fleetflow-db

# RabbitMQ logs
docker logs -f fleetflow-mq
```

---

## 🛑 Stopping Services

### Stop Local Services

```bash
# Ctrl+C in Terminal 1 (API)
# Ctrl+C in Terminal 2 (Worker)
```

### Stop Infrastructure

```bash
# Stop and remove containers
docker-compose down

# Stop but keep data
docker-compose stop

# Restart infrastructure
docker-compose up -d
```

---

## 🐛 Troubleshooting

### "Connection refused" error

```
Error: Cannot connect to database/RabbitMQ
```

**Solution:** Ensure `docker-compose up -d` is running

```bash
docker-compose ps  # Check status
docker-compose up -d  # Restart if needed
```

### "ModuleNotFoundError: No module named 'pika'"

```
Error: No module named 'pika'
```

**Solution:** Virtual environment not activated or dependencies not installed

```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Install deps
```

### Worker not processing messages

```
🔄 Processing trip: ...
❌ Trip not found in database
```

**Solution:** Database schema not initialized

```bash
docker-compose down -v  # Remove volumes
docker-compose up -d    # Restart with fresh schema
```

### Port already in use

```
Error: Address already in use
```

**Solution:** Kill process using port

```bash
# Port 8000 (FastAPI)
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Port 5432 (PostgreSQL)
lsof -i :5432 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Port 5672 (RabbitMQ)
lsof -i :5672 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

---

## 📁 File Structure

```
project-fleetflow/
├── .env                          # Local environment variables
├── docker-compose.yml            # Infrastructure only (PostgreSQL + RabbitMQ)
├── DEVELOPMENT.md                # This file
├── test_handshake.py             # Integration test script
│
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # (Optional) For production builds
│   └── src/
│       ├── main.py               # FastAPI service (run locally)
│       ├── worker.py             # RabbitMQ consumer (run locally)
│       ├── models.py             # Pydantic schemas
│       └── analytics.py          # Safety scoring logic
│
└── sql/
    └── init.sql                  # Database initialization
```

---

## ✅ Next Steps

1. ✅ Run `docker-compose up -d`
2. ✅ Run `python -m uvicorn src.main:app --reload` in Terminal 1
3. ✅ Run `python src/worker.py` in Terminal 2
4. ✅ Run `python test_handshake.py` in Terminal 3
5. 📝 Start building features!

Happy developing! 🚀
