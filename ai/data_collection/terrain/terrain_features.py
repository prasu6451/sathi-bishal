"""
Terrain feature extraction & validation routines.
Handles elevation, slope, aspect, curvature, and Topographic Wetness Index (TWI).
"""

from typing import Dict, Optional, Any
import numpy as np


def validate_terrain_data(terrain_dict: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """
    Validate terrain parameters (elevation, slope, aspect, curvature, twi).

    Args:
        terrain_dict: Dictionary containing terrain variables.

    Returns:
        Validated terrain dictionary.
    """
    keys = ["elevation", "slope", "aspect", "curvature", "twi"]
    validated = {}

    for key in keys:
        val = terrain_dict.get(key)
        if val is not None:
            try:
                fval = float(val)
                if key == "slope":
                    # Slope between 0 and 90 degrees
                    fval = max(0.0, min(90.0, fval))
                elif key == "aspect":
                    # Aspect between 0 and 360 degrees
                    fval = fval % 360.0
                validated[key] = fval
            except (ValueError, TypeError):
                validated[key] = None
        else:
            validated[key] = None

    return validated


def calculate_twi(specific_catchment_area: float, slope_deg: float) -> Optional[float]:
    """
    Compute Topographic Wetness Index (TWI) = ln(a / tan(beta)).

    Args:
        specific_catchment_area: Specific catchment area (m^2/m)
        slope_deg: Slope in degrees

    Returns:
        TWI value or None if slope is invalid/zero.
    """
    if slope_deg <= 0.0 or specific_catchment_area <= 0.0:
        return 0.0

    slope_rad = np.radians(slope_deg)
    tan_slope = np.tan(slope_rad)
    if tan_slope <= 0.0:
        return 0.0

    twi = np.log(specific_catchment_area / tan_slope)
    return float(round(twi, 4))
