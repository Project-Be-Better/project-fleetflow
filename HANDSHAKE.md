# FleetFlow - Basic Handshake Implementation

## ✅ What's Implemented

### 1. **Database Layer** ([sql/init.sql](sql/init.sql))

- `telemetry.trip_logs`: Stores raw telemetry data with status tracking
- `telemetry.driver_scores`: Stores calculated safety metrics
- Proper indexing and foreign keys for performance

### 2. **Shared Models** ([backend/src/models.py](backend/src/models.py))

- `TelemetryPoint`: Individual sensor reading
- `TripPayload`: API request schema
- `TripIngestResponse`: 202 Accepted response
- `DriverScore`: Analysis result schema

### 3. **Analytics Engine** ([backend/src/analytics.py](backend/src/analytics.py))

- `calculate_safety_score()`: NumPy-powered scoring logic
- Detects harsh braking (g_force < -0.4)
- Detects rapid acceleration (g_force > 0.4)
- Penalty system: -5 points per harsh event

### 4. **FastAPI Producer** ([backend/src/main.py](backend/src/main.py))

- `POST /api/v1/telemetry`: Async ingestion endpoint (returns 202)
- `GET /api/v1/trip/{trip_id}/score`: Retrieves calculated scores
- Implements **Claim Check Pattern**: Stores full blob, publishes only UUID
- Automatic RabbitMQ queue publishing

### 5. **RabbitMQ Consumer** ([backend/src/worker.py](backend/src/worker.py))

- Consumes trip IDs from queue
- Fetches telemetry blob from database
- Runs analytics pipeline
- Stores results in `driver_scores` table
- Updates trip status: PENDING → PROCESSING → COMPLETED

### 6. **Infrastructure** ([docker-compose.yml](docker-compose.yml))

- PostgreSQL 15 with automatic schema initialization
- RabbitMQ 3.12 with management UI
- FastAPI service on port 8000
- Python worker service

---

## 🚀 How to Run the Handshake

### 1. Start the services

```bash
docker-compose up -d
```

### 2. Verify services are healthy

```bash
docker-compose ps
docker logs fleetflow-db      # Check database is ready
docker logs fleetflow-mq      # Check RabbitMQ is ready
docker logs fleetflow-api     # Check API is running
```

### 3. Run the handshake test

```bash
pip install aiohttp  # One-time dependency for test script
python test_handshake.py
```

---

## 📊 Expected Output

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
   Created: 2025-01-01T12:00:00.000Z

============================================================
✅ HANDSHAKE SUCCESSFUL!
============================================================
```

---

## 🔄 Data Flow Diagram

```
┌─────────────┐
│   Vehicle   │ POST /api/v1/telemetry
└──────┬──────┘
       │ (telemetry + timestamp)
       ↓
┌──────────────────────┐
│   FastAPI (main.py)  │
│  - Validate request  │
│  - Store blob        │ → CLAIM CHECK PATTERN
│  - Publish trip_id   │
└──────────┬───────────┘
           │ 202 ACCEPTED
           ↓ (trip_id)
       [Client]

    ┌──────────────────────┐
    │  PostgreSQL          │
    │ trip_logs (PENDING)  │
    └──────────────────────┘
           ↑
           │ Fetch
    ┌──────────────────────┐
    │  RabbitMQ Queue      │
    │ [trip_id, trip_id]   │
    └──────────┬───────────┘
               │ Consume
               ↓
    ┌──────────────────────┐
    │  Worker (worker.py)  │
    │  - Fetch blob        │
    │  - Calculate score   │
    │  - Insert results    │
    └──────────┬───────────┘
               ↓
    ┌──────────────────────────────┐
    │  PostgreSQL                  │
    │ driver_scores (COMPLETED)    │
    │ trip_logs (COMPLETED)        │
    └──────────┬───────────────────┘
               │
       GET /api/v1/trip/{trip_id}/score
               │
               ↓
           [Client gets score]
```

---

## 🧪 Test the Endpoints Manually

### Submit telemetry

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

### Retrieve score (after ~1-2s)

```bash
curl http://localhost:8000/api/v1/trip/{trip_id}/score
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

---

## 📋 What's Next (Future Iterations)

1. **Frontend Dashboard** (React + Vite)

   - Display fleet vehicle list
   - Show driver scores
   - Trend analysis over time

2. **Advanced Analytics**

   - Machine learning driver behavior classification
   - Predictive maintenance scoring
   - Route optimization

3. **Scaling & Performance**

   - Connection pooling for PostgreSQL
   - Batch processing worker
   - Distributed processing with Celery

4. **Deployment**
   - Kubernetes manifests
   - CI/CD pipeline
   - Production monitoring with Prometheus/Grafana
