import os
import json
import random
import numpy as np
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
import pika

from models import TripPayload, TripIngestResponse, TripDataRaw, TripStatus, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/fleetflow"
)
# SQLAlchemy needs the driver name explicitly if not using the default psycopg2
if "postgresql://" in DATABASE_URL and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "telemetry_analysis"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# RabbitMQ connection
rabbitmq_connection = None
rabbitmq_channel = None


def get_db():
    """FastAPI dependency to provide a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def setup_rabbitmq():
    """Initializes RabbitMQ connection and channel."""
    global rabbitmq_connection, rabbitmq_channel
    try:
        parameters = pika.URLParameters(RABBITMQ_URL)
        rabbitmq_connection = pika.BlockingConnection(parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_declare(queue=QUEUE_NAME, durable=True)
        print("✅ RabbitMQ connection established.")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ Could not connect to RabbitMQ: {e}")
        # You might want to handle this more gracefully, e.g., by exiting
        rabbitmq_connection = None
        rabbitmq_channel = None


def publish_to_queue(trip_id: str):
    """Publishes trip_id to RabbitMQ queue in a blocking manner."""
    if not rabbitmq_channel or not rabbitmq_channel.is_open:
        print("🐰 RabbitMQ channel not available, attempting to reconnect...")
        setup_rabbitmq()

    if rabbitmq_channel:
        rabbitmq_channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=trip_id,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print(f"📥 Published trip_id {trip_id} to queue '{QUEUE_NAME}'.")
    else:
        # This will be caught by the endpoint's error handling
        raise ConnectionError("Failed to publish to RabbitMQ: channel not available.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    print("🚀 FastAPI service starting up...")
    Base.metadata.create_all(bind=engine)
    setup_rabbitmq()
    yield
    # Shutdown
    if rabbitmq_connection and rabbitmq_connection.is_open:
        rabbitmq_connection.close()
        print("🔌 RabbitMQ connection closed.")
    print("🛑 FastAPI service shutting down.")


app = FastAPI(
    title="FleetFlow Telemetry Ingestion API",
    description="API for vehicle telemetry ingestion using the Claim Check pattern.",
    lifespan=lifespan,
)


@app.post("/api/v1/telemetry", response_model=TripIngestResponse, status_code=202)
async def ingest_telemetry(payload: TripPayload, db: Session = Depends(get_db)):
    """
    If payload.data is empty, generates 5,000 synthetic points for testing.
    """
    try:
        telemetry_data = [p.model_dump() for p in payload.data]

        # Synthetic Data Generation for Testing
        if not telemetry_data:
            print(
                "🧪 Empty payload detected. Generating 5,000 synthetic points using NumPy..."
            )
            n_points = 5000

            # Vectorized generation
            accels = np.random.uniform(-0.5, 0.5, n_points)
            lat_forces = np.random.uniform(-0.1, 0.1, n_points)

            # Calculate speeds: speed = max(0, cumsum(accel * gravity_to_kmh))
            # Assuming 1Hz sampling (1 second between points)
            speeds = np.maximum(0, np.cumsum(accels * 9.81 * 3.6))

            # Convert to list of dicts for JSON serialization
            telemetry_data = [
                {
                    "speed_kmh": float(round(s, 2)),
                    "g_force_long": float(round(a, 3)),
                    "g_force_lat": float(round(l, 3)),
                }
                for s, a, l in zip(speeds, accels, lat_forces)
            ]

        # Step 1: Create and persist the TripDataRaw entity
        trip = TripDataRaw(
            vehicle_id=payload.vehicle_id,
            driver_id=payload.driver_id,
            start_time=payload.timestamp,
            end_time=payload.timestamp,
            raw_telemetry_blob={"data": telemetry_data},
            status=TripStatus.PENDING_ANALYSIS,
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)

        # Step 2: Publish the new trip's ID to the queue for the worker to process.
        # Use run_in_threadpool to avoid blocking the event loop.
        await run_in_threadpool(publish_to_queue, str(trip.id))

        return TripIngestResponse(
            status="QUEUED_FOR_ANALYSIS",
            trip_id=trip.id,
        )
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")
    except Exception as e:
        # Rollback in case of other errors during publish etc.
        db.rollback()
        print(f"❌ Error during telemetry ingestion: {e}")
        raise HTTPException(status_code=500, detail="Failed to ingest telemetry data.")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/trip/{trip_id}/status")
async def get_trip_status(trip_id: UUID, db: Session = Depends(get_db)):
    """Retrieve the current processing status of a trip."""
    trip = db.query(TripDataRaw).filter(TripDataRaw.id == trip_id).one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found.")
    return {
        "trip_id": trip.id,
        "status": trip.status.value,
        "last_updated": trip.created_at,
    }
