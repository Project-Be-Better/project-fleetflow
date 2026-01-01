import json
import numpy as np
from typing import Dict, List, Any
from datetime import datetime


def calculate_safety_score(telemetry_blob: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate safety score from telemetry data.

    Score calculation:
    - Base: 100
    - Penalty per harsh braking event (-2): g_force_long < -0.4
    - Penalty per rapid acceleration (-2): g_force_long > 0.4
    - Penalty per harsh cornering (-2): abs(g_force_lat) > 0.3
    - Penalty per speeding event (> 80km/h): -2 base
    - Weather/Time Multipliers:
        - Rainy: 2x penalty
        - Night (20:00-06:00): 1.5x penalty (rounded)

    Consecutive points above threshold are counted as a single event.
    """
    if not telemetry_blob or "data" not in telemetry_blob:
        return {
            "safety_score": 100,
            "harsh_braking_count": 0,
            "rapid_accel_count": 0,
        }

    data = telemetry_blob.get("data", [])
    if not data:
        return {"safety_score": 100, "harsh_braking_count": 0, "rapid_accel_count": 0}

    # Extract values
    g_long = np.array([p.get("g_force_long", 0) for p in data])
    g_lat = np.array([p.get("g_force_lat", 0) for p in data])
    speeds = np.array([p.get("speed_kmh", 0) for p in data])

    def get_event_indices(series, threshold, operator="gt"):
        """Returns the starting indices of consecutive sequences above/below threshold."""
        if operator == "gt":
            active = series > threshold
        elif operator == "lt":
            active = series < threshold
        elif operator == "abs":
            active = np.abs(series) > threshold
        else:
            active = series > threshold

        # Find transitions from False to True
        diff = np.diff(active.astype(int))
        indices = np.where(diff == 1)[0] + 1
        if active[0]:
            indices = np.insert(indices, 0, 0)
        return indices

    # Get indices of events
    braking_idx = get_event_indices(g_long, -0.4, "lt")
    accel_idx = get_event_indices(g_long, 0.4, "gt")
    cornering_idx = get_event_indices(g_lat, 0.3, "abs")
    speeding_idx = get_event_indices(speeds, 80, "gt")

    def is_night(ts_str):
        try:
            dt = datetime.fromisoformat(ts_str)
            return dt.hour >= 20 or dt.hour < 6
        except:
            return False

    # Calculate penalty based on weather and time at each event index
    def calculate_penalty(indices, base_penalty=2):
        penalty = 0
        for idx in indices:
            point = data[idx]
            weather = point.get("weather", "clear")
            ts = point.get("timestamp")

            current_penalty = base_penalty

            # Multipliers
            if weather == "rainy":
                current_penalty *= 2
            if is_night(ts):
                current_penalty *= 1.5

            penalty += int(current_penalty)
        return penalty

    total_penalty = (
        calculate_penalty(braking_idx)
        + calculate_penalty(accel_idx)
        + calculate_penalty(cornering_idx)
        + calculate_penalty(speeding_idx)
    )

    # --- Updated Scoring Logic ---
    # We use a floor of 40 for the pilot to keep scores realistic.
    # We also apply a 0.5 multiplier to the total penalty so that
    # aggressive drivers land in the 40-60 range instead of hitting 0.
    safety_score = max(40, 100 - int(total_penalty * 0.5))

    # Summary for return
    harsh_braking = len(braking_idx)
    rapid_accel = len(accel_idx)
    harsh_cornering = len(cornering_idx)
    speeding_events = len(speeding_idx)
    max_speed = float(np.max(speeds))

    # --- NEW: Odometer & Utilization Metrics ---
    # Total Distance from Odometer
    first_odo = data[0].get("odometer_km", 0)
    last_odo = data[-1].get("odometer_km", 0)
    total_distance = float(max(0, last_odo - first_odo))

    # Total Driving Duration (Active Time)
    # We calculate the time difference between consecutive points.
    # If the gap is > 5 minutes, we assume the car was parked.
    total_driving_seconds = 0
    for i in range(1, len(data)):
        try:
            ts1 = datetime.fromisoformat(
                data[i - 1].get("timestamp").replace("Z", "+00:00")
            )
            ts2 = datetime.fromisoformat(
                data[i].get("timestamp").replace("Z", "+00:00")
            )
            delta = (ts2 - ts1).total_seconds()
            if 0 < delta < 300:  # 5 minutes threshold for "active"
                total_driving_seconds += delta
        except Exception as e:
            continue

    total_duration_hrs = float(total_driving_seconds / 3600.0)
    avg_speed = float(
        total_distance / total_duration_hrs if total_duration_hrs > 0 else 0
    )

    # Calculate actual rental span from data
    try:
        first_ts = datetime.fromisoformat(
            data[0].get("timestamp").replace("Z", "+00:00")
        )
        last_ts = datetime.fromisoformat(
            data[-1].get("timestamp").replace("Z", "+00:00")
        )
        actual_span_hrs = (last_ts - first_ts).total_seconds() / 3600.0
    except:
        actual_span_hrs = 48.0

    # Utilization (use the larger of 48h or actual span to be safe)
    rental_duration_hrs = max(48.0, actual_span_hrs)
    utilization_pct = float(min(100, (total_duration_hrs / rental_duration_hrs) * 100))

    return {
        "safety_score": safety_score,
        "harsh_braking_count": harsh_braking,
        "rapid_accel_count": rapid_accel,
        "harsh_cornering_count": harsh_cornering,
        "speeding_count": speeding_events,
        "max_speed": max_speed,
        "total_distance": total_distance,
        "avg_speed": avg_speed,
        "total_duration_hrs": total_duration_hrs,
        "utilization_pct": utilization_pct,
        "weather_summary": f"Started {data[0].get('weather')}, ended {data[-1].get('weather')}",
    }
