import enum
from pydantic import BaseModel, Field
from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy import (
    Float,
    create_engine,
    Column,
    String,
    DateTime,
    JSON,
    Enum,
    Integer,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base, sessionmaker


# ============================================
# DATABASE SETUP (SQLAlchemy ORM)
# ============================================

Base = declarative_base()


class TripStatus(enum.Enum):
    """Enumeration for the status of a trip analysis."""

    PENDING_ANALYSIS = "PENDING_ANALYSIS"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TripDataRaw(Base):
    """
    SQLAlchemy ORM model for the 'trip_data_raw' table in the 'telemetry' schema.
    """

    __tablename__ = "trip_data_raw"
    __table_args__ = {"schema": "telemetry"}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    vehicle_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    driver_id = Column(PG_UUID(as_uuid=True), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    raw_telemetry_blob = Column(JSON, nullable=False)
    status = Column(
        Enum(TripStatus, name="trip_status_enum", schema="telemetry"),
        nullable=False,
        default=TripStatus.PENDING_ANALYSIS,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DriverScoreDB(Base):
    """
    SQLAlchemy ORM model for the 'driver_scores' table in the 'telemetry' schema.
    """

    __tablename__ = "driver_scores"
    __table_args__ = {"schema": "telemetry"}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    trip_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("telemetry.trip_data_raw.id"),
        unique=True,
        nullable=False,
    )
    vehicle_id = Column(PG_UUID(as_uuid=True), nullable=False)
    driver_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    safety_score = Column(Integer, nullable=False)
    max_speed = Column(Float, default=0)
    harsh_braking_count = Column(Integer, default=0)
    rapid_accel_count = Column(Integer, default=0)
    harsh_cornering_count = Column(Integer, default=0)
    speeding_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# ============================================
# API MODELS (Pydantic)
# ============================================


class TelemetryPoint(BaseModel):
    """Individual telemetry data point"""

    timestamp: datetime
    latitude: float
    longitude: float
    speed_kmh: float
    g_force_long: float  # Longitudinal (0.4g = ~4 m/s²)
    g_force_lat: float  # Lateral
    weather: str = "clear"


class TripPayload(BaseModel):
    """Incoming telemetry submission"""

    vehicle_id: UUID
    driver_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: List[TelemetryPoint]


class TripIngestResponse(BaseModel):
    """Response when trip is accepted"""

    status: str
    trip_id: UUID


class DriverScore(BaseModel):
    """Driver scoring result"""

    trip_id: UUID
    safety_score: int
    harsh_braking_count: int
    max_speed: float
    rapid_accel_count: int
    harsh_cornering_count: int
    created_at: datetime
