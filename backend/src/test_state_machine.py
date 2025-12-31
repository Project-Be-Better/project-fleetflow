import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch
import uuid

# Make sure models can be found
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app, get_db
from models import Base, TripDataRaw, TripStatus
from worker import TelemetryWorker

# ======================================================================================
# TEST SETUP
# ======================================================================================

# Use an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the in-memory database
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Dependency override for tests to use the in-memory SQLite database."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Apply the override to the FastAPI app
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Fixture to get a clean database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.query(TripDataRaw).delete()
        db.commit()
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client():
    """Fixture to get a FastAPI test client."""
    with TestClient(app) as c:
        yield c


# ======================================================================================
# TESTS
# ======================================================================================


def test_telemetry_state_machine_success_path(client, db_session):
    """
    Tests the full state machine transition from PENDING -> PROCESSING -> COMPLETED.
    """
    # --- Part 1: API Ingestion ---
    # Call the API to create a trip. It should be created with PENDING_ANALYSIS status.
    test_payload = {
        "vehicle_id": str(uuid.uuid4()),
        "driver_id": str(uuid.uuid4()),
        "data": [{"speed_kmh": 60, "g_force_long": 0, "g_force_lat": 0}],
    }

    # Mock the RabbitMQ call in main.py since we are not testing RabbitMQ itself
    with patch("main.run_in_threadpool") as mock_publish:
        response = client.post("/api/v1/telemetry", json=test_payload)
        mock_publish.assert_called_once()

    assert response.status_code == 202
    response_data = response.json()
    trip_id = response_data["trip_id"]
    assert response_data["status"] == "QUEUED_FOR_ANALYSIS"

    # --- Part 2: Verify Initial State in DB ---
    # The trip should be in the database with the initial "PENDING_ANALYSIS" state.
    trip_in_db = db_session.query(TripDataRaw).filter(TripDataRaw.id == trip_id).one()
    assert trip_in_db is not None
    assert trip_in_db.status == TripStatus.PENDING_ANALYSIS
    print(f"\n✅ [SUCCESS] Initial state is PENDING_ANALYSIS for trip {trip_id}")

    # --- Part 3: Worker Simulation ---
    # Simulate the worker consuming the message for the created trip.
    worker = TelemetryWorker()
    worker.SessionLocal = TestingSessionLocal  # Point worker to test DB

    mock_channel = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = 123
    
    # The body of the message is the trip_id as a string
    message_body = str(trip_id).encode("utf-8")

    worker.process_message(mock_channel, mock_method, None, message_body)

    # --- Part 4: Verify Final State in DB ---
    # The worker should have updated the trip's status to "COMPLETED".
    db_session.refresh(trip_in_db)
    assert trip_in_db.status == TripStatus.COMPLETED
    print(f"✅ [SUCCESS] Final state is COMPLETED for trip {trip_id}")

    # The worker should have acknowledged the message
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)


def test_telemetry_state_machine_failure_path(client, db_session):
    """
    Tests the state machine transition to FAILED when an error occurs.
    """
    # --- Part 1 & 2: API Ingestion and Initial State Verification ---
    test_payload = {
        "vehicle_id": str(uuid.uuid4()),
        "driver_id": str(uuid.uuid4()),
        "data": [{"speed_kmh": 60, "g_force_long": 0, "g_force_lat": 0}],
    }
    with patch("main.run_in_threadpool") as mock_publish:
        response = client.post("/api/v1/telemetry", json=test_payload)
    trip_id = response.json()["trip_id"]

    trip_in_db = db_session.query(TripDataRaw).filter(TripDataRaw.id == trip_id).one()
    assert trip_in_db.status == TripStatus.PENDING_ANALYSIS
    print(f"\n✅ [FAILURE] Initial state is PENDING_ANALYSIS for trip {trip_id}")

    # --- Part 3: Worker Simulation with Failure ---
    # Patch the analytics function to raise an exception.
    with patch("worker.calculate_safety_score", side_effect=ValueError("Test Exception")):
        worker = TelemetryWorker()
        worker.SessionLocal = TestingSessionLocal

        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = 456
        message_body = str(trip_id).encode("utf-8")

        worker.process_message(mock_channel, mock_method, None, message_body)

    # --- Part 4: Verify Final State in DB ---
    # The worker should have caught the exception and updated the status to "FAILED".
    db_session.refresh(trip_in_db)
    assert trip_in_db.status == TripStatus.FAILED
    print(f"✅ [FAILURE] Final state is FAILED for trip {trip_id}")

    # The worker should still acknowledge the message to prevent requeueing
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)
