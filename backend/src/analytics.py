import json
import numpy as np
from typing import Dict, List, Any


def calculate_safety_score(telemetry_blob: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate safety score from telemetry data.

    Score calculation:
    - Base: 100
    - Penalty per harsh braking event (-5): g_force_long < -0.4
    - Penalty per rapid acceleration (-5): g_force_long > 0.4

    Returns dict with safety metrics.
    """
    if not telemetry_blob or "data" not in telemetry_blob:
        return {
            "safety_score": 100,
            "harsh_braking_count": 0,
            "rapid_accel_count": 0,
        }

    data = telemetry_blob.get("data", [])

    # Extract g-force values
    g_forces_long = [point.get("g_force_long", 0) for point in data]

    # Count harsh events
    harsh_braking = sum(1 for gf in g_forces_long if gf < -0.4)
    rapid_accel = sum(1 for gf in g_forces_long if gf > 0.4)

    # Calculate score
    total_harsh_events = harsh_braking + rapid_accel
    safety_score = max(0, 100 - (total_harsh_events * 5))

    return {
        "safety_score": safety_score,
        "harsh_braking_count": harsh_braking,
        "rapid_accel_count": rapid_accel,
    }
