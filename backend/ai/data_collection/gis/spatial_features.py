"""
GIS spatial distance metrics and validation helpers.
Calculates geographic proximity to roads, streams, faults, bridges, hospitals, and settlements.
"""

import math
from typing import Dict, Optional, Any


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance between two GPS coordinates in meters.

    Args:
        lat1, lon1: First coordinate (deg)
        lat2, lon2: Second coordinate (deg)

    Returns:
        Distance in meters.
    """
    r = 6371000.0  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2 +
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def validate_infrastructure_data(infra_dict: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Validate proximity distance fields to key infrastructure elements.

    Args:
        infra_dict: Raw infrastructure dictionary.

    Returns:
        Validated non-negative distance metrics (in meters).
    """
    keys = [
        "distance_to_road_m",
        "distance_to_stream_m",
        "distance_to_bridge_m",
        "distance_to_hospital_m",
        "distance_to_village_m"
    ]
    validated = {}

    for key in keys:
        val = infra_dict.get(key)
        if val is not None:
            try:
                fval = float(val)
                validated[key] = max(0.0, fval)
            except (ValueError, TypeError):
                validated[key] = None
        else:
            validated[key] = None

    return validated
