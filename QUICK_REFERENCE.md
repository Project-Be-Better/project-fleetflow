# Quick Reference - Hybrid Development

## 🚀 One-Time Setup

```bash
# macOS/Linux
chmod +x dev-setup.sh
./dev-setup.sh

# Windows
dev-setup.bat

# OR manual setup
docker-compose up -d
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ⚡ Start Development

**Terminal 1 - Infrastructure:**

```bash
docker-compose up -d
```

**Terminal 2 - FastAPI (auto-reload on save):**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python -m uvicorn src.main:app --reload
```

**Terminal 3 - Worker:**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python src/worker.py
```

**Terminal 4 - Test:**

```bash
python test_handshake.py
```

---

## 📍 Important URLs

| Service     | URL                        | Purpose        |
| ----------- | -------------------------- | -------------- |
| API         | http://localhost:8000      | Main server    |
| Swagger     | http://localhost:8000/docs | Test endpoints |
| RabbitMQ UI | http://localhost:15672     | Monitor queues |
| Database    | localhost:5432             | PostgreSQL     |

---

## 📝 Quick API Tests

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
  }' | jq .
```

### Get Score (after ~1s)

```bash
curl http://localhost:8000/api/v1/trip/YOUR_TRIP_ID/score | jq .
```

### Health Check

```bash
curl http://localhost:8000/health
```

---

## 🛑 Stop Services

```bash
# Local services: Press Ctrl+C in each terminal

# Infrastructure: Stop but keep data
docker-compose stop

# Infrastructure: Full shutdown (removes containers)
docker-compose down

# Infrastructure: Full shutdown + remove data
docker-compose down -v
```

---

## 🐛 Troubleshooting Cheat Sheet

| Issue                 | Solution                                        |
| --------------------- | ----------------------------------------------- |
| `Connection refused`  | Run `docker-compose up -d`                      |
| `ModuleNotFoundError` | Activate venv: `source venv/bin/activate`       |
| `Port already in use` | See DEVELOPMENT.md section 🛑 Stopping Services |
| `Trip not found`      | Wait 1-2s for worker to process                 |
| FastAPI not reloading | Check changes saved & watch terminal            |

---

## 📊 Check Status

```bash
# Docker containers
docker-compose ps

# Database tables
psql postgresql://postgres:password@localhost:5432/fleetflow -c "\dt telemetry.*"

# RabbitMQ queues
curl -u guest:guest http://localhost:15672/api/queues

# Container logs
docker logs fleetflow-db
docker logs fleetflow-mq
```

---

## 🔄 Development Cycle

1. **Edit** code in `backend/src/`
2. **Save** (Ctrl+S)
3. **Watch** for "Reloading..." in Terminal 2
4. **Test** via Swagger or curl
5. **Repeat**

No Docker rebuild needed! ⚡

---

## 📚 Full Guides

- **Complete Setup**: See `DEVELOPMENT.md`
- **Architecture**: See `HANDSHAKE.md`
- **Project Overview**: See `README.md`

---

**Happy coding!** 🚀
