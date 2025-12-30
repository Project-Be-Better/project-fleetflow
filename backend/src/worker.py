import os
import json
import time
from uuid import UUID

import pika
import psycopg
from psycopg import sql

from analytics import calculate_safety_score

# Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:password@localhost:5432/fleetflow"
)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "telemetry_analysis"


class TelemetryWorker:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect_db(self):
        """Establish database connection"""
        return psycopg.connect(DATABASE_URL)

    def connect_rabbitmq(self):
        """Establish RabbitMQ connection"""
        parameters = pika.URLParameters(RABBITMQ_URL)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
        return self.channel

    def process_message(self, ch, method, properties, body):
        """
        Consume and process a telemetry analysis message.

        Flow:
        1. Decode trip_id from message
        2. Fetch telemetry blob from database
        3. Calculate safety score using analytics
        4. Insert results into driver_scores table
        5. Update trip status to COMPLETED
        6. Acknowledge message
        """
        trip_id = body.decode("utf-8")
        print(f"🔄 Processing trip: {trip_id}")

        try:
            with self.connect_db() as conn:
                # Step 1: Update status to PROCESSING
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE telemetry.trip_logs SET status = %s WHERE id = %s",
                        ("PROCESSING", trip_id),
                    )
                    conn.commit()

                # Step 2: Fetch telemetry blob
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT telemetry_blob FROM telemetry.trip_logs WHERE id = %s",
                        (trip_id,),
                    )
                    result = cur.fetchone()
                    if not result:
                        print(f"❌ Trip {trip_id} not found in database")
                        ch.basic_nack(delivery_tag=method.delivery_tag)
                        return

                    telemetry_blob = result[0]

                # Step 3: Calculate safety score
                metrics = calculate_safety_score(telemetry_blob)
                print(f"📊 Calculated metrics: {metrics}")

                # Step 4: Insert driver score
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO telemetry.driver_scores "
                        "(trip_id, safety_score, harsh_braking_count, rapid_accel_count) "
                        "VALUES (%s, %s, %s, %s)",
                        (
                            trip_id,
                            metrics["safety_score"],
                            metrics["harsh_braking_count"],
                            metrics["rapid_accel_count"],
                        ),
                    )
                    conn.commit()

                # Step 5: Update trip status to COMPLETED
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE telemetry.trip_logs SET status = %s WHERE id = %s",
                        ("COMPLETED", trip_id),
                    )
                    conn.commit()

            print(f"✅ Successfully processed trip: {trip_id}")

            # Step 6: Acknowledge message (remove from queue)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"❌ Error processing trip {trip_id}: {e}")
            # Requeue message on error
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

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

            print(f"🚀 Worker listening on queue: {QUEUE_NAME}")
            print("Press CTRL+C to stop")
            self.channel.start_consuming()

        except KeyboardInterrupt:
            print("\n⛔ Worker stopping...")
            self.connection.close()
        except Exception as e:
            print(f"❌ Worker error: {e}")
            self.connection.close()


if __name__ == "__main__":
    worker = TelemetryWorker()
    worker.start()
