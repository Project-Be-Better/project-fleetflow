from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from datetime import datetime


class TelemetryPoint(BaseModel):
    """Individual telemetry data point"""

    speed_kmh: float
    g_force_long: float  # Longitudinal (0.4g = ~4 m/s²)
    g_force_lat: float  # Lateral


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
    rapid_accel_count: int
    created_at: datetime
