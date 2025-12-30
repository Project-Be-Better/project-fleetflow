import os
import asyncio
import json
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pika
import psycopg
from psycopg import AsyncConnection, sql

from models import TripPayload, TripIngestResponse

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5432/fleetflow"
)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "telemetry_analysis"

# Global connection pool
db_pool = None
rabbitmq_connection = None
rabbitmq_channel = None


async def init_db():
    """Initialize database connection pool"""
    global db_pool
    db_pool = await psycopg.AsyncConnection.connect(DATABASE_URL)


def init_rabbitmq():
    """Initialize RabbitMQ connection and declare queue"""
    global rabbitmq_connection, rabbitmq_channel
    credentials = pika.PlainCredentials("guest", "guest")
    parameters = pika.ConnectionParameters(host="localhost", credentials=credentials)
    rabbitmq_connection = pika.BlockingConnection(parameters)
    rabbitmq_channel = rabbitmq_connection.channel()
    rabbitmq_channel.queue_declare(queue=QUEUE_NAME, durable=True)


async def publish_to_queue(trip_id: str):
    """Publish trip_id to RabbitMQ queue"""
    try:
        rabbitmq_channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=trip_id,
            properties=pika.BasicProperties(delivery_mode=2),  # Persistent
        )
    except Exception as e:
        print(f"Error publishing to queue: {e}")
        raise


async def save_trip_log(payload: TripPayload) -> UUID:
    """Save trip log to database and return trip_id"""
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        result = await conn.execute(
            sql.SQL(
                "INSERT INTO telemetry.trip_logs (vehicle_id, driver_id, timestamp, telemetry_blob, status) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING id"
            ),
            [
                str(payload.vehicle_id),
                str(payload.driver_id),
                payload.timestamp,
                json.dumps({"data": [p.model_dump() for p in payload.data]}),
                "PENDING",
            ],
        )
        trip_id = (await result.fetchone())[0]
        await conn.commit()
    return UUID(trip_id)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown"""
    # Startup
    await init_db()
    init_rabbitmq()
    print("✅ FastAPI service started (Producer mode)")
    yield
    # Shutdown
    if db_pool:
        await db_pool.close()
    if rabbitmq_connection:
        rabbitmq_connection.close()
    print("✅ FastAPI service shutdown")


app = FastAPI(
    title="FleetFlow Telemetry Ingestion API",
    description="High-performance async API for vehicle telemetry ingestion",
    lifespan=lifespan,
)


@app.post("/api/v1/telemetry", response_model=TripIngestResponse, status_code=202)
async def ingest_telemetry(payload: TripPayload):
    """
    Accept telemetry data using the Claim Check pattern.

    1. Validates and stores the full telemetry blob in the database
    2. Publishes the trip_id to RabbitMQ for async processing
    3. Returns immediately with 202 ACCEPTED
    """
    try:
        # Step 1: Persist telemetry to database
        trip_id = await save_trip_log(payload)

        # Step 2: Publish trip_id to queue for processing
        await publish_to_queue(str(trip_id))

        return TripIngestResponse(
            status="QUEUED",
            trip_id=trip_id,
        )
    except Exception as e:
        print(f"Error ingesting telemetry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/v1/trip/{trip_id}/score")
async def get_trip_score(trip_id: str):
    """Retrieve driver score for a specific trip"""
    try:
        async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
            result = await conn.execute(
                sql.SQL(
                    "SELECT trip_id, safety_score, harsh_braking_count, rapid_accel_count, created_at "
                    "FROM telemetry.driver_scores WHERE trip_id = %s"
                ),
                [trip_id],
            )
            row = await result.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Score not found. Processing may still be in progress.",
            )

        return {
            "trip_id": str(row[0]),
            "safety_score": row[1],
            "harsh_braking_count": row[2],
            "rapid_accel_count": row[3],
            "created_at": row[4],
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
