import json
import numpy as np
from typing import Dict, List, Any


def calculate_safety_score(telemetry_blob: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate safety score from telemetry data.

    Score calculation:
    - Base: 100
    - Penalty per harsh braking event (-2): g_force_long < -0.4
    - Penalty per rapid acceleration (-2): g_force_long > 0.4
    - Penalty per harsh cornering (-2): abs(g_force_lat) > 0.3

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

    def count_events(series, threshold, operator="gt"):
        """Counts consecutive sequences above/below threshold as single events."""
        if operator == "gt":
            active = series > threshold
        elif operator == "lt":
            active = series < threshold
        else:
            active = np.abs(series) > threshold

        # Find transitions from False to True
        diff = np.diff(active.astype(int))
        count = np.sum(diff == 1)
        # Check if the first point is active
        if active[0]:
            count += 1
        return int(count)

    # Count events
    harsh_braking = count_events(g_long, -0.4, "lt")
    rapid_accel = count_events(g_long, 0.4, "gt")
    harsh_cornering = count_events(g_lat, 0.3, "abs")
    max_speed = float(max(p.get("speed_kmh", 0) for p in data))

    # Calculate score
    # 2 points penalty per event
    total_penalty = (harsh_braking + rapid_accel + harsh_cornering) * 2
    safety_score = max(0, 100 - total_penalty)

    return {
        "safety_score": safety_score,
        "harsh_braking_count": harsh_braking,
        "rapid_accel_count": rapid_accel,
        "harsh_cornering_count": harsh_cornering,
        "max_speed": max_speed,
    }
