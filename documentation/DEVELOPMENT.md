# FleetFlow - Local Development Setup (Docker Approach)

## 🎯 Architecture

- **Infrastructure:** PostgreSQL + RabbitMQ
- **Services:** FastAPI API + Python Worker

Everything runs inside Docker containers. This ensures a consistent environment across Windows, Mac, and Linux, avoiding OS-specific issues like event loop conflicts.

---

## 🚀 Quick Start

### 1. Start Everything

```bash
# Build and start all services
docker-compose up --build -d

# Verify services are running
docker-compose ps
```

### 2. View Logs

```bash
# Follow logs for all services
docker-compose logs -f

# Or specific services
docker-compose logs -f api
docker-compose logs -f worker
```

### 3. Run Integration Test

You can run the test locally to verify the full handshake:

```bash
# Navigate to backend and run test
cd backend
.\venv\Scripts\Activate.ps1
python ..\test_handshake.py
```

---

## 🛠️ Development Workflow

### Hot Reloading

The `api` service is configured with `--reload` and volumes. When you edit code in `backend/src/`, the container will automatically restart the server.

### Database Access

- **Host:** `localhost` (from your machine) or `postgres` (from other containers)
- **Port:** `5432`
- **User:** `postgres`
- **Password:** `password`
- **Database:** `fleetflow`

### RabbitMQ Management UI

Access the dashboard at [http://localhost:15672](http://localhost:15672)

- **User:** `guest`
- **Password:** `guest`

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
2. **FastAPI auto-reloads** (watch for `Reloading` message in `docker-compose logs -f api`)
3. **Test in VS Code** or with curl/Postman
4. **Worker picks up changes** automatically (Note: Worker might need a manual restart if not using a reloader: `docker-compose restart worker`)

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

### Retrieve Score

```bash
curl http://localhost:8000/api/v1/trip/{trip_id}/score
```

---

## 🚦 Monitoring Infrastructure

### PostgreSQL

```bash
# Connect to database from host
psql postgresql://postgres:password@localhost:5432/fleetflow
```

### RabbitMQ Management UI

Open **http://localhost:15672** in browser

- Username: `guest`
- Password: `guest`

---

## 🛑 Stopping Services

```bash
# Stop and remove containers
docker-compose down

# Stop but keep data
docker-compose stop
```

---

## 📁 File Structure

```
project-fleetflow/
├── docker-compose.yml            # Full stack (DB, MQ, API, Worker)
├── documentation/
│   └── DEVELOPMENT.md            # This file
├── test_handshake.py             # Integration test script
│
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Service image definition
│   └── src/
│       ├── main.py               # FastAPI service
│       ├── worker.py             # RabbitMQ consumer
│       ├── models.py             # Pydantic schemas
│       └── analytics.py          # Safety scoring logic
│
└── sql/
    └── init.sql                  # Database initialization
```

Happy developing! 🚀
