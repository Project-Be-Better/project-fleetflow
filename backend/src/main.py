import os
import json
import random
import numpy as np
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
import pika

from models import TripPayload, TripIngestResponse, TripDataRaw, TripStatus, Base
from state_manager import TripStateManager
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

# Enable CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Frontend
# Try local path first, then container path
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if not os.path.exists(frontend_path):
    frontend_path = "/app/frontend"

if os.path.exists(frontend_path):
    app.mount(
        "/dashboard", StaticFiles(directory=frontend_path, html=True), name="frontend"
    )


@app.get("/")
async def root():
    if os.path.exists(os.path.join(frontend_path, "index.html")):
        return FileResponse(os.path.join(frontend_path, "index.html"))
    return {"message": "FleetFlow API is running. Dashboard not found."}


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

            # --- NEW: Driver Profiles for Score Variety ---
            # 50% Safe, 30% Moderate, 20% Aggressive
            profile = np.random.choice(
                ["safe", "moderate", "aggressive"], p=[0.5, 0.3, 0.2]
            )

            if profile == "safe":
                n_range = (0, 2)
                speed_base = 30
                accel_noise = 0.02
            elif profile == "moderate":
                n_range = (2, 6)
                speed_base = 60
                accel_noise = 0.04
            else:  # aggressive
                n_range = (8, 15)
                speed_base = 85
                accel_noise = 0.1

            # Use a normal distribution for realistic "smooth" driving
            accels = np.random.normal(0, accel_noise, n_points)
            lat_forces = np.random.normal(0, 0.02, n_points)

            # Inject "harsh" events based on profile
            n_braking = np.random.randint(*n_range)
            braking_indices = np.random.choice(n_points, n_braking, replace=False)
            accels[braking_indices] = np.random.uniform(-0.6, -0.45, n_braking)

            n_accel = np.random.randint(*n_range)
            accel_indices = np.random.choice(n_points, n_accel, replace=False)
            accels[accel_indices] = np.random.uniform(0.45, 0.6, n_accel)

            n_corner = np.random.randint(*n_range)
            corner_indices = np.random.choice(n_points, n_corner, replace=False)
            lat_forces[corner_indices] = np.random.choice(
                [-0.4, 0.4], n_corner
            ) * np.random.uniform(1.1, 1.3, n_corner)

            # Calculate speeds: speed = max(0, cumsum(accel * gravity_to_kmh))
            # We'll add a base speed and some smoothing to make it look like a real trip
            speeds = np.maximum(
                0, speed_base + np.cumsum(accels * 9.81 * 3.6 * 0.1)
            )  # Reduced multiplier for stability
            # Clip speed to realistic highway limits
            speeds = np.clip(speeds, 0, 120)

            print(
                f"  - Generated {profile} trip with {n_braking} braking, {n_accel} accel, {n_corner} cornering events."
            )

            # --- NEW: Contextual Data Generation ---
            # 1. Timestamps (1 second intervals)
            start_ts = payload.timestamp
            # 30% chance to make it a night trip for testing
            if np.random.random() < 0.3:
                # Set to a random hour between 20:00 and 04:00
                night_hour = np.random.choice([20, 21, 22, 23, 0, 1, 2, 3, 4])
                start_ts = start_ts.replace(
                    hour=night_hour, minute=np.random.randint(0, 60)
                )

            timestamps = [start_ts + timedelta(seconds=i) for i in range(n_points)]

            # 2. GPS Coordinates (Singapore Bounding Box)
            # Start at a random point in SG
            base_lat, base_lon = 1.3521, 103.8198  # Central SG
            lats = base_lat + np.cumsum(np.random.normal(0, 0.0001, n_points))
            lons = base_lon + np.cumsum(np.random.normal(0, 0.0001, n_points))

            # 3. Dynamic Weather (Transitions)
            # Start with one condition, potentially transition halfway
            weather_options = ["clear", "rainy", "cloudy"]
            start_weather = np.random.choice(weather_options, p=[0.7, 0.2, 0.1])

            # Create an array of weather conditions
            weather_conditions = [start_weather] * n_points
            if np.random.random() < 0.3:  # 30% chance of weather change during trip
                change_point = np.random.randint(n_points // 4, 3 * n_points // 4)
                new_weather = np.random.choice(
                    [w for w in weather_options if w != start_weather]
                )
                for i in range(change_point, n_points):
                    weather_conditions[i] = new_weather

            # Convert to list of dicts for JSON serialization
            telemetry_data = [
                {
                    "timestamp": ts.isoformat(),
                    "latitude": float(round(lat, 6)),
                    "longitude": float(round(lon, 6)),
                    "speed_kmh": float(round(s, 2)),
                    "g_force_long": float(round(a, 3)),
                    "g_force_lat": float(round(l, 3)),
                    "weather": w,
                }
                for ts, lat, lon, s, a, l, w in zip(
                    timestamps,
                    lats,
                    lons,
                    speeds,
                    accels,
                    lat_forces,
                    weather_conditions,
                )
            ]

        # Step 1: Create and persist the TripDataRaw entity using StateManager
        state_mgr = TripStateManager(db)
        trip = state_mgr.initialize_trip(
            vehicle_id=payload.vehicle_id,
            driver_id=payload.driver_id,
            start_time=payload.timestamp,
            raw_data={"data": telemetry_data},
        )

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


@app.get("/api/v1/trip/{trip_id}/results")
async def get_trip_results(trip_id: UUID, db: Session = Depends(get_db)):
    """Retrieve the analysis results for a completed trip."""
    from models import DriverScoreDB

    score = (
        db.query(DriverScoreDB).filter(DriverScoreDB.trip_id == trip_id).one_or_none()
    )
    if not score:
        # Check if trip exists but not yet completed
        trip = db.query(TripDataRaw).filter(TripDataRaw.id == trip_id).one_or_none()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found.")
        return {
            "trip_id": trip_id,
            "status": trip.status.value,
            "message": "Results not yet available.",
        }

    return {
        "trip_id": score.trip_id,
        "safety_score": score.safety_score,
        "max_speed": score.max_speed,
        "harsh_braking_count": score.harsh_braking_count,
        "rapid_accel_count": score.rapid_accel_count,
        "harsh_cornering_count": score.harsh_cornering_count,
        "speeding_count": score.speeding_count,
        "created_at": score.created_at,
    }
