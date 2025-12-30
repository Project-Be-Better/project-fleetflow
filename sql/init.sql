-- Create telemetry schema
CREATE SCHEMA IF NOT EXISTS telemetry;

-- Table: trip_logs (Raw Telemetry Data)
CREATE TABLE IF NOT EXISTS telemetry.trip_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id UUID NOT NULL,
    driver_id UUID NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    telemetry_blob JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Table: driver_scores (Analysis Results)
CREATE TABLE IF NOT EXISTS telemetry.driver_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID NOT NULL UNIQUE REFERENCES telemetry.trip_logs(id),
    safety_score INT CHECK (safety_score >= 0 AND safety_score <= 100),
    harsh_braking_count INT DEFAULT 0,
    rapid_accel_count INT DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (trip_id) REFERENCES telemetry.trip_logs(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_trip_logs_vehicle_id ON telemetry.trip_logs(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_trip_logs_driver_id ON telemetry.trip_logs(driver_id);
CREATE INDEX IF NOT EXISTS idx_trip_logs_status ON telemetry.trip_logs(status);
CREATE INDEX IF NOT EXISTS idx_driver_scores_trip_id ON telemetry.driver_scores(trip_id);
