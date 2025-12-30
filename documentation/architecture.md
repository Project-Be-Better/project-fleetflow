# FleetFlow Module 1: Telematics & Driver Scoring Engine (Python Prototype)

## 1. Executive Summary

This module implements a high-throughput, event-driven pipeline for ingesting vehicle telemetry data and generating automated driver safety scores.

For the initial prototype phase, we are utilizing a **Pure Python Architecture** (FastAPI + RabbitMQ) to maximize development velocity and leverage shared data models (Pydantic) between the API and ML layers, while maintaining a strict logical separation of concerns suitable for future scaling.

**Primary Goal:** Enable "Zero-Touch" fleet operations where driver behavior is analyzed instantly upon trip completion without human intervention.

---

## 2. Project Structure (Monorepo)

```text
fleet-flow-proto/
├── docs/                      # Documentation & Architecture
│   └── architecture/
│
├── sql/                       # Database Initialization
│   └── init.sql               # Schema definitions (telemetry schema)
│
├── backend/                   # 🐍 THE BRAIN (FastAPI + Worker)
│   ├── src/
│   │   ├── main.py            # Service A: API Endpoints (Ingestion)
│   │   ├── worker.py          # Service B: RabbitMQ Consumer (Processing)
│   │   ├── analytics.py       # Core Logic: NumPy Vector Math
│   │   └── models.py          # Shared Pydantic Schemas
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/                  # ⚛️ THE FACE (React + Tailwind)
│   ├── src/
│   │   ├── components/        # UI Components (Charts, Grids)
│   │   ├── hooks/             # Data Fetching (React Query)
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
│
└── docker-compose.yml         # Orchestrator (DB + MQ + Backend)

```

---

## 3. Architectural Design

### 3.1 The "Claim Check" Pattern

To handle high-frequency telemetry data (simulated at 16kHz or large JSON arrays) without clogging the messaging infrastructure, we implement the **Claim Check Pattern**:

1. **The Check (Payload):** The heavy JSON blob is stored immediately in the database by the **FastAPI Ingest Service**.
2. **The Claim (Reference):** Only the lightweight `trip_id` (UUID) is sent through the message broker (**RabbitMQ**).
3. **The Retrieval:** The **Python Worker** consumes the ID and fetches the actual payload from the database for processing.

### 3.2 System Components

| Component          | Technology         | Role               | Justification                                                                                            |
| ------------------ | ------------------ | ------------------ | -------------------------------------------------------------------------------------------------------- |
| **Ingestion API**  | **FastAPI**        | Producer / Gateway | High-performance Python async framework. Validates incoming JSON using shared Pydantic models.           |
| **Message Broker** | **RabbitMQ**       | Middleware         | Decouples ingestion from processing. Ensures the API remains responsive even if the ML worker is busy.   |
| **ML Worker**      | **Python + NumPy** | Consumer / Worker  | Runs in a background process (or separate container). Uses NumPy for vectorized scoring calculations.    |
| **Persistence**    | **PostgreSQL 15**  | Database           | Relational integrity for metadata + `JSONB` support for storing unstructured telemetry logs efficiently. |
| **Frontend**       | **React + Vite**   | Dashboard          | Provides the operator interface to view fleet status and driver scores.                                  |

---

## 4. Data Flow Specification

### Phase A: Ingestion (Synchronous)

1. **Trigger:** Vehicle/Simulator sends `POST /api/v1/telemetry` with a JSON payload containing `vehicle_id`, `driver_id`, and `telemetry_data`.
2. **Validation:** FastAPI uses `models.TripPayload` to validate data types immediately.
3. **Persist:** FastAPI creates a record in `telemetry.trip_logs` with status `PENDING_ANALYSIS`.
4. **Acknowledge:** System responds `202 ACCEPTED` to the client immediately. The client **does not** wait for the ML result.

### Phase B: Asynchronous Processing

5. **Signal:** FastAPI publishes the `trip_id` to the `telemetry_analysis` queue in RabbitMQ.
6. **Consume:** The `worker.py` process picks up the message.
7. **Fetch:** Worker queries `telemetry.trip_logs` using the ID to retrieve the `telemetry_data` blob.
8. **Compute:** `analytics.py` vectorizes the data to calculate:

- **Safety Score (0-100):** Base 100 minus penalties.
- **Harsh Events:** Count of G-force < -0.4g (Braking) or > 0.4g (Acceleration).

9. **Result:** Worker inserts the final metrics into `telemetry.driver_scores`.
10. **Finalize:** Worker updates `telemetry.trip_logs` status to `COMPLETED`.

---

## 5. Database Schema (Schema: `telemetry`)

We use a separate schema to isolate high-volume sensor data from future core business logic.

### 5.1 Table: `trip_logs` (The Raw Data)

- **`id` (UUID, PK):** Unique Trip Identifier.
- **`telemetry_blob` (JSONB):** The raw sensor array.
- _Structure:_ `[{"t": 1200, "spd": 85, "gx": 0.5}, ...]`

- **`status` (VARCHAR):** State machine tracker (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).

### 5.2 Table: `driver_scores` (The Insight)

- **`trip_id` (UUID, FK):** Links back to the raw log.
- **`safety_score` (INT):** Normalized 0-100 rating.
- **`harsh_braking_count` (INT):** Specific risk metric.
- **`rapid_accel_count` (INT):** Specific risk metric.

---

## 6. API Interface Specification

### Endpoint: Submit Telemetry

**URL:** `POST /api/v1/telemetry`
**Content-Type:** `application/json`

**Request Body (Pydantic Model):**

```json
{
  "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
  "driver_id": "c9284200-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": [
    { "speed_kmh": 45, "g_force_long": 0.1, "g_force_lat": 0.0 },
    { "speed_kmh": 45, "g_force_long": -0.5, "g_force_lat": 0.0 }
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

## 7. Development Roadmap (Vertical Slice #1)

1. **Infrastructure:** Provision Postgres and RabbitMQ via Docker Compose. [✅ Planned]
2. **Database:** Execute `init.sql` to create `telemetry` schema and tables.
3. **Backend Core:**

- Create shared `models.py` (Pydantic).
- Implement `main.py` (FastAPI Producer).
- Implement `worker.py` (RabbitMQ Consumer).

4. **Backend Math:** Implement `analytics.py` (NumPy logic).
5. **Frontend:** Scaffold React + Vite app to fetch and display the scores.
6. **Simulation:** Run Python script to generate synthetic driving data and verify the full pipeline.
