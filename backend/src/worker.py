import os
import json
import time
from uuid import UUID

import pika
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics import calculate_safety_score
from models import TripDataRaw, TripStatus, DriverScoreDB
from state_manager import TripStateManager

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:password@localhost:5432/fleetflow"
)
if "postgresql://" in DATABASE_URL and "+psycopg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "telemetry_analysis"


class TelemetryWorker:
    def __init__(self):
        # Database setup
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # RabbitMQ connection setup
        self.connection = None
        self.channel = None

    def connect_rabbitmq(self):
        """Establish RabbitMQ connection"""
        parameters = pika.URLParameters(RABBITMQ_URL)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
        print(f"✅ RabbitMQ connection established. Listening on queue: {QUEUE_NAME}")

    def process_message(self, ch, method, properties, body):
        """
        Consume and process a telemetry analysis message using a state machine approach.

        Flow:
        1. Decode trip_id from message.
        2. Set trip status to PROCESSING.
        3. Perform analysis.
        4. On success, set status to COMPLETED and save score.
        5. On failure, set status to FAILED.
        6. Acknowledge the message to remove it from the queue.
        """
        try:
            trip_id = UUID(body.decode("utf-8"))
            print(f"🔄 Received trip for processing: {trip_id}")
        except (ValueError, TypeError) as e:
            print(f"❌ Invalid message body: {body}. Error: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        db = self.SessionLocal()
        state_mgr = TripStateManager(db)
        trip = None
        try:
            # Fetch the trip from the database
            trip = state_mgr.get_trip(trip_id)

            if not trip:
                print(
                    f"❓ Trip {trip_id} not found in database. Acknowledging message."
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # === STATE MACHINE: PENDING -> PROCESSING ===
            state_mgr.transition_to(trip_id, TripStatus.PROCESSING)

            # Perform the core analysis on the raw data
            metrics = calculate_safety_score(trip.raw_telemetry_blob)
            print(f"  - 📊 Calculated metrics: {metrics}")

            # Save the score to the 'driver_scores' table
            score_entry = DriverScoreDB(
                trip_id=trip.id,
                vehicle_id=trip.vehicle_id,
                driver_id=trip.driver_id,
                safety_score=metrics["safety_score"],
                harsh_braking_count=metrics["harsh_braking_count"],
                rapid_accel_count=metrics["rapid_accel_count"],
                harsh_cornering_count=metrics.get("harsh_cornering_count", 0),
                speeding_count=metrics.get("speeding_count", 0),
                max_speed=metrics["max_speed"],
                avg_speed=metrics.get("avg_speed", 0),
                total_distance=metrics.get("total_distance", 0),
            )
            db.add(score_entry)

            # === STATE MACHINE: PROCESSING -> COMPLETED ===
            state_mgr.transition_to(trip_id, TripStatus.COMPLETED)
            print(
                f"✅ Successfully processed trip: {trip_id}. Status set to COMPLETED."
            )

        except Exception as e:
            print(f"❌ Error during processing of trip {trip_id}: {e}")
            if trip:
                # === STATE MACHINE: (ANY) -> FAILED ===
                db.rollback()
                state_mgr.transition_to(trip_id, TripStatus.FAILED)
                print(f"  - ❗ Trip {trip_id} status set to FAILED.")
        finally:
            if db:
                db.close()
            # Acknowledge the message regardless of success or failure
            # to prevent it from being re-queued endlessly.
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """Start consuming from RabbitMQ queue"""
        try:
            self.connect_rabbitmq()
            self.channel.basic_qos(prefetch_count=1)  # Process one message at a time
            self.channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=self.process_message,
                auto_ack=False,
            )
            print("Press CTRL+C to stop worker.")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print("\n⛔ Worker stopping...")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ RabbitMQ connection error: {e}. Check RabbitMQ is running.")
        finally:
            if self.connection and self.connection.is_open:
                self.connection.close()


if __name__ == "__main__":
    worker = TelemetryWorker()
    worker.start()
