from sqlalchemy.orm import Session
from models import TripDataRaw, TripStatus
from uuid import UUID
from datetime import datetime


class TripStateManager:
    """
    Centralized manager for handling trip state transitions and audit logging.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_trip(self, trip_id: UUID) -> TripDataRaw:
        return (
            self.db.query(TripDataRaw).filter(TripDataRaw.id == trip_id).one_or_none()
        )

    def transition_to(self, trip_id: UUID, new_status: TripStatus) -> TripDataRaw:
        """
        Transitions a trip to a new status.
        In the future, we can add validation logic here (e.g., can't go from COMPLETED to PROCESSING).
        """
        trip = self.get_trip(trip_id)
        if not trip:
            print(f"⚠️ StateManager: Trip {trip_id} not found.")
            return None

        old_status = trip.status
        trip.status = new_status

        # We could add an audit log entry here if we had a TripHistory table
        print(
            f"🔄 State Transition: Trip {trip_id} | {old_status.value} -> {new_status.value}"
        )

        self.db.commit()
        self.db.refresh(trip)
        return trip

    def initialize_trip(
        self, vehicle_id: UUID, driver_id: UUID, start_time: datetime, raw_data: dict
    ) -> TripDataRaw:
        """
        Creates a new trip in PENDING_ANALYSIS state.
        """
        trip = TripDataRaw(
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            start_time=start_time,
            end_time=start_time,  # Will be updated later
            raw_telemetry_blob=raw_data,
            status=TripStatus.PENDING_ANALYSIS,
        )
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        print(f"🆕 Trip Initialized: {trip.id} (PENDING_ANALYSIS)")
        return trip
