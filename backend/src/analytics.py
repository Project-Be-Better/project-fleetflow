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

    safety_score = max(0, 100 - total_penalty)

    # Summary for return
    harsh_braking = len(braking_idx)
    rapid_accel = len(accel_idx)
    harsh_cornering = len(cornering_idx)
    speeding_events = len(speeding_idx)
    max_speed = float(np.max(speeds))

    return {
        "safety_score": safety_score,
        "harsh_braking_count": harsh_braking,
        "rapid_accel_count": rapid_accel,
        "harsh_cornering_count": harsh_cornering,
        "speeding_count": speeding_events,
        "max_speed": max_speed,
        "weather_summary": f"Started {data[0].get('weather')}, ended {data[-1].get('weather')}",
    }
