# FleetFlow - Telematics & Driver Scoring Engine

> 📁 **Documentation Note:** All guides (DEVELOPMENT.md, SETUP_VALIDATION.md, etc.) have been organized into the [`documentation/`](documentation/) folder. See [documentation/INDEX.md](documentation/INDEX.md) for complete navigation.

A high-throughput, event-driven pipeline for ingesting vehicle telemetry data and generating automated driver safety scores using a **Hybrid Development Approach**.

## 🎯 Overview

**FleetFlow** is a Python-based microservices architecture that demonstrates a vertical slice of a fleet management system:

- **Ingestion API** (FastAPI) - Accept telemetry data with instant 202 ACCEPTED response
- **Message Queue** (RabbitMQ) - Decouple ingestion from processing using the Claim Check pattern
- **Worker Service** (Python) - Asynchronously analyze telemetry and calculate safety scores
- **Data Persistence** (PostgreSQL) - Store raw telemetry and computed results

### Key Features

✅ High-throughput async ingestion API  
✅ Claim Check pattern for large payloads  
✅ RabbitMQ-based async processing  
✅ NumPy-powered safety scoring  
✅ Hybrid local + Docker development setup  
✅ Single API handshake across vertical slice

---

## 🚀 Quick Start (Hybrid Approach)

**Infrastructure in Docker** | **Code Runs Locally**

```bash
# 1. Clone and navigate
git clone <repo-url>
cd project-fleetflow

# 2. Automated setup (macOS/Linux)
chmod +x dev-setup.sh
./dev-setup.sh

# OR manual setup for all platforms
docker-compose up -d                          # Start PostgreSQL + RabbitMQ
cd backend && python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# 3. Run services locally (Terminal 1)
python -m uvicorn src.main:app --reload

# 4. Run worker (Terminal 2)
python src/worker.py

# 5. Test end-to-end (Terminal 3)
pip install aiohttp
python test_handshake.py
```

---

## 📚 Documentation

**All documentation is organized in the [documentation/](documentation/) folder.**

**→ Start with [documentation/INDEX.md](documentation/INDEX.md) for the complete guide**

Quick links:

- 🚀 [START_HERE.md](documentation/START_HERE.md) - 5-minute quick start
- ⚡ [QUICK_REFERENCE.md](documentation/QUICK_REFERENCE.md) - Daily commands & URLs
- 📖 [DEVELOPMENT.md](documentation/DEVELOPMENT.md) - Complete setup & troubleshooting
- 🏗️ [HANDSHAKE.md](documentation/HANDSHAKE.md) - API & architecture
- ✅ [SETUP_VALIDATION.md](documentation/SETUP_VALIDATION.md) - Verification checklist

```
Vehicle Telemetry
       ↓
   [FastAPI]  ← Instant 202 ACCEPTED
   Store Blob → [PostgreSQL]
       ↓
   Publish ID ↓
             [RabbitMQ Queue]
                    ↓
                 [Worker]
              Fetch Blob ↓
              Calculate Score
              Store Results
```

### Why This Approach?

| Aspect                  | Benefit                                               |
| ----------------------- | ----------------------------------------------------- |
| **Async Processing**    | API stays responsive even if worker is slow           |
| **Claim Check Pattern** | Handle large telemetry without clogging message queue |
| **Hybrid Setup**        | Instant reload on code changes + easy debugging       |
| **Vertical Slice**      | Complete end-to-end functionality in one feature      |

---

## 🔌 API Endpoints

### Submit Telemetry (Ingestion)

```http
POST /api/v1/telemetry
Content-Type: application/json

{
  "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
  "driver_id": "c9284200-e29b-41d4-a716-446655440000",
  "timestamp": "2025-01-01T12:00:00Z",
  "data": [
    {"speed_kmh": 50, "g_force_long": 0.1, "g_force_lat": 0},
    {"speed_kmh": 55, "g_force_long": -0.5, "g_force_lat": 0}
  ]
}
```

**Response (202 Accepted):**

```json
{
  "status": "QUEUED",
  "trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Retrieve Score (Results)

```http
GET /api/v1/trip/{trip_id}/score
```

**Response:**

```json
{
  "trip_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "safety_score": 90,
  "harsh_braking_count": 1,
  "rapid_accel_count": 1,
  "created_at": "2025-01-01T12:00:01Z"
}
```

---

## 🧪 Testing

```bash
# Automated integration test (includes handshake verification)
python test_handshake.py

# Manual testing with curl
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H "Content-Type: application/json" \
  -d '{"vehicle_id":"550e8400-e29b-41d4-a716-446655440000",...}'

# View Swagger/OpenAPI docs
open http://localhost:8000/docs
```

---

## 📊 Monitoring

| Tool            | Access                     | Purpose        |
| --------------- | -------------------------- | -------------- |
| **Swagger UI**  | http://localhost:8000/docs | Test endpoints |
| **RabbitMQ UI** | http://localhost:15672     | Monitor queues |
| **PostgreSQL**  | psql on port 5432          | Query data     |

---

## 📁 Project Structure

```
project-fleetflow/
├── README.md                      # This file
├── DEVELOPMENT.md                 # Local dev guide (READ THIS!)
├── HANDSHAKE.md                   # Architecture & API details
├── docker-compose.yml             # Infrastructure (Postgres + RabbitMQ)
├── dev-setup.sh / dev-setup.bat   # Automated setup scripts
├── .env                           # Environment variables
├── .gitignore                     # Git exclusions
├── test_handshake.py              # Integration test
│
├── backend/
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # (for production builds)
│   └── src/
│       ├── main.py                # FastAPI ingestion service
│       ├── worker.py              # RabbitMQ consumer
│       ├── models.py              # Pydantic schemas
│       └── analytics.py           # Safety scoring logic
│
├── sql/
│   └── init.sql                   # Database initialization
│
├── documentation/
│   ├── architecture.md            # System design document
│   └── architecture/              # Diagram files
│
└── frontend/                      # (Coming soon)
    └── React + Vite application
```

---

## 🛠️ Technology Stack

| Layer         | Technology        | Role                         |
| ------------- | ----------------- | ---------------------------- |
| **API**       | FastAPI + Uvicorn | Async HTTP server            |
| **Queue**     | RabbitMQ          | Message broker               |
| **Database**  | PostgreSQL 15     | Persistent storage           |
| **Worker**    | Python + NumPy    | Async processing & analytics |
| **Container** | Docker Compose    | Local infrastructure         |

---

## 🚦 Development Workflow

1. **Edit code** in `backend/src/`
2. **FastAPI auto-reloads** on save (watch terminal for `Reloading`)
3. **Test changes** via Swagger UI or curl
4. **Worker auto-picks up** new messages from queue
5. **Commit & push** when ready

---

## 🐛 Troubleshooting

**See [documentation/DEVELOPMENT.md](documentation/DEVELOPMENT.md) for detailed troubleshooting guide**

Common issues:

- Database connection refused → Run `docker-compose up -d`
- Port already in use → See documentation/DEVELOPMENT.md cleanup section
- Module not found → Activate venv and reinstall: `pip install -r requirements.txt`

---

## 📝 Next Steps

- [ ] Read [documentation/START_HERE.md](documentation/START_HERE.md) for quick orientation
- [ ] Read [documentation/DEVELOPMENT.md](documentation/DEVELOPMENT.md) for complete setup
- [ ] Run `python test_handshake.py` to verify end-to-end
- [ ] Explore [documentation/HANDSHAKE.md](documentation/HANDSHAKE.md) for architecture details
- [ ] Check Swagger UI at http://localhost:8000/docs
- [ ] Build additional features on this vertical slice

---

## 📄 License

MIT
