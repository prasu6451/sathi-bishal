"""
Rainfall feature extraction utilities for landslide risk estimation.
Handles cumulative rainfall windows (1h, 24h, 3d, 7d, 14d) and Antecedent Rainfall Index (ARI).
"""

from typing import Dict, Optional, Any
import numpy as np


def validate_rainfall_data(rainfall_dict: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Validate and extract standard rainfall metrics (1h, 24h, 3d, 7d, 14d).

    Args:
        rainfall_dict: Nested rainfall dictionary from JSON record.

    Returns:
        Dictionary of validated float values (or None for missing).
    """
    keys = ["rain_1h", "rain_24h", "rain_3d", "rain_7d", "rain_14d"]
    validated = {}

    for key in keys:
        val = rainfall_dict.get(key)
        if val is not None:
            try:
                float_val = float(val)
                # Rainfall cannot be negative
                validated[key] = max(0.0, float_val)
            except (ValueError, TypeError):
                validated[key] = None
        else:
            validated[key] = None

    return validated


def calculate_antecedent_rainfall_index(
    rain_24h: Optional[float],
    rain_3d: Optional[float],
    rain_7d: Optional[float],
    decay_factor: float = 0.8
) -> Optional[float]:
    """
    Compute Antecedent Rainfall Index (ARI) using exponentially weighted cumulative rainfall.

    Args:
        rain_24h: 24-hour rainfall in mm
        rain_3d: 3-day cumulative rainfall in mm
        rain_7d: 7-day cumulative rainfall in mm
        decay_factor: Daily decay coefficient (default 0.8)

    Returns:
        Computed ARI value or None if inputs missing.
    """
    if rain_24h is None or rain_3d is None or rain_7d is None:
        return None

    # Estimate daily breakdown from cumulative metrics
    day1 = rain_24h
    day2_3 = max(0.0, rain_3d - rain_24h) / 2.0
    day4_7 = max(0.0, rain_7d - rain_3d) / 4.0

    ari = (
        day1 * (decay_factor ** 0) +
        day2_3 * (decay_factor ** 1 + decay_factor ** 2) +
        day4_7 * (decay_factor ** 3 + decay_factor ** 4 + decay_factor ** 5 + decay_factor ** 6)
    )
    return round(float(ari), 2)
