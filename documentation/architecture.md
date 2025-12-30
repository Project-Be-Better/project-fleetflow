# FleetFlow Module 1: Telematics & Driver Scoring Engine

```
fleet-flow-proto/
├── docs/                      # Documentation
│   └── architecture/
│
├── sql/                       # Database Scripts
│   └── init.sql
│
├── backend/                   # 🐍 THE BRAIN (FastAPI + Worker)
│   ├── src/
│   │   ├── main.py            # API Endpoints
│   │   ├── worker.py          # RabbitMQ Consumer
│   │   ├── analytics.py       # NumPy Logic
│   │   └── models.py          # Pydantic Schemas
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/                  # ⚛️ THE FACE (React + Tailwind)
│   ├── src/
│   │   ├── components/        # UI (Charts, Grids)
│   │   ├── hooks/             # API Calls (useTelemetry)
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile             # (Optional for dev, good for prod)
│
└── docker-compose.yml         # Orchestrator (DB + MQ + Backend)
```

## 1. Executive Summary

This module implements a high-throughput, event-driven pipeline for ingesting vehicle telemetry data and generating automated driver safety scores. It moves beyond standard CRUD operations by integrating a **polyglot microservices architecture** (Java & Python) to leverage the best tools for transactional stability and mathematical computation.

**Primary Goal:** Enable "Zero-Touch" fleet operations where driver behavior is analyzed instantly upon trip completion without human intervention.

---

## 2. Architectural Design

### 2.1 The "Claim Check" Pattern

To handle high-frequency telemetry data (simulated at 16kHz or large JSON arrays) without clogging the messaging infrastructure, we implement the **Claim Check Pattern**:

1. **The Check (Payload):** The heavy JSON blob is stored immediately in the database by the Ingestion Service (Spring Boot).
2. **The Claim (Reference):** Only the lightweight `trip_id` (UUID) is sent through the message broker (RabbitMQ).
3. **The Retrieval:** The Worker Service (FastAPI) uses the ID to fetch the actual payload from the database for processing.

### 2.2 System Components

| Component             | Technology          | Role               | Justification                                                                                                    |
| --------------------- | ------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------- |
| **Ingestion Service** | **Spring Boot 3**   | Producer / Gateway | Provides robust type safety, validation, and high-concurrency handling for incoming HTTP requests.               |
| **Message Broker**    | **RabbitMQ**        | Middleware         | Decouples ingestion from processing. Ensures data is not lost if the ML service is down or under heavy load.     |
| **ML Engine**         | **FastAPI + NumPy** | Consumer / Worker  | Python ecosystem offers superior libraries for vector math (`numpy`) and ML (future `scikit-learn` integration). |
| **Persistence**       | **PostgreSQL 15**   | Database           | Relational integrity for metadata + `JSONB` support for storing unstructured telemetry logs efficiently.         |

---

## 3. Data Flow Specification

### Phase A: Ingestion (Synchronous)

1. **Trigger:** Vehicle/Simulator sends `POST /api/v1/telemetry` with a JSON payload containing `vehicle_id`, `driver_id`, and `telemetry_data` (array of speed, G-force, timestamp).
2. **Persist:** Spring Boot creates a record in `telemetry.trip_logs` with status `PENDING_ANALYSIS`.
3. **Acknowledge:** System responds `202 ACCEPTED` to the client immediately. The client does not wait for analysis.

### Phase B: Asynchronous Processing

4. **Signal:** Spring Boot publishes the `trip_id` to the `telemetry_analysis` queue in RabbitMQ.
5. **Consume:** The FastAPI worker picks up the message.
6. **Fetch:** Worker queries `telemetry.trip_logs` using the ID to retrieve the `telemetry_data` blob.
7. **Compute:** NumPy vectorizes the data to calculate:

- **Safety Score (0-100):** Base 100 minus penalties.
- **Harsh Events:** Count of G-force < -0.4g (Braking) or > 0.4g (Acceleration).

8. **Result:** Worker inserts the final metrics into `telemetry.driver_scores`.
9. **Finalize:** Worker updates `telemetry.trip_logs` status to `COMPLETED`.

---

## 4. Database Schema (Schema: `telemetry`)

We use a separate schema to isolate high-volume sensor data from future core business logic.

### 4.1 Table: `trip_logs` (The Raw Data)

- **`id` (UUID, PK):** Unique Trip Identifier.
- **`telemetry_blob` (JSONB):** The raw sensor array.
- _Structure:_ `[{"t": 1200, "spd": 85, "gx": 0.5}, ...]`

- **`status` (VARCHAR):** State machine tracker (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).

### 4.2 Table: `driver_scores` (The Insight)

- **`trip_id` (UUID, FK):** Links back to the raw log.
- **`safety_score` (INT):** Normalized 0-100 rating.
- **`harsh_braking_count` (INT):** Specific risk metric.
- **`rapid_accel_count` (INT):** Specific risk metric.

---

## 5. API Interface Specification

### Endpoint: Submit Telemetry

**URL:** `POST /api/v1/telemetry`
**Content-Type:** `application/json`

**Request Body:**

```json
{
  "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
  "driver_id": "c9284200-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": [
    { "speed_kmh": 45, "g_force_long": 0.1, "g_force_lat": 0.0 },
    { "speed_kmh": 45, "g_force_long": -0.5, "g_force_lat": 0.0 },
    ...
  ]
}

```

**Success Response (202 Accepted):**

```json
{
  "status": "QUEUED",
  "trip_id": "a1b2c3d4-..."
}
```

---

## 6. Development Roadmap (Vertical Slice #1)

1. **Infrastructure:** Provision Postgres and RabbitMQ via Docker Compose. [✅ Planned]
2. **Database:** Execute `init.sql` to create `telemetry` schema and tables.
3. **Spring Boot:** Implement Controller and RabbitMQ Producer.
4. **FastAPI:** Implement Consumer and NumPy Logic.
5. **Simulation:** Run Python script to generate synthetic driving data and verify the full pipeline.
