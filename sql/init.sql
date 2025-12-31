-- Create the schema for telemetry data if it doesn't already exist.
CREATE SCHEMA IF NOT EXISTS telemetry;

-- Drop the enum type if it exists to ensure a clean slate, then create it.
-- This is useful for development to apply changes to the enum.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trip_status_enum') THEN
        DROP TYPE telemetry.trip_status_enum;
    END IF;
END$$;

CREATE TYPE telemetry.trip_status_enum AS ENUM (
    'PENDING_ANALYSIS',
    'PROCESSING',
    'COMPLETED',
    'FAILED'
);

-- Create the table to store raw trip data.
-- This table name 'trip_data_raw' matches the SQLAlchemy ORM model.
CREATE TABLE IF NOT EXISTS telemetry.trip_data_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    raw_telemetry_blob JSONB NOT NULL,
    status telemetry.trip_status_enum NOT NULL DEFAULT 'PENDING_ANALYSIS',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes to optimize query performance, especially for the worker.
CREATE INDEX IF NOT EXISTS idx_trip_data_raw_vehicle_id ON telemetry.trip_data_raw(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_trip_data_raw_status ON telemetry.trip_data_raw(status);

-- The 'driver_scores' table stores the results of the analysis.
CREATE TABLE IF NOT EXISTS telemetry.driver_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL UNIQUE REFERENCES telemetry.trip_data_raw(id) ON DELETE CASCADE,
    vehicle_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    max_speed FLOAT DEFAULT 0,
    safety_score INT CHECK (safety_score >= 0 AND safety_score <= 100),
    harsh_braking_count INT DEFAULT 0,
    rapid_accel_count INT DEFAULT 0,
    harsh_cornering_count INT DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_driver_scores_driver_id ON telemetry.driver_scores(driver_id);
CREATE INDEX IF NOT EXISTS idx_driver_scores_trip_id ON telemetry.driver_scores(trip_id);
