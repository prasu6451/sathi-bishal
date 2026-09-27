"""
Real-Time Feature Assembler Service.
Combines Static Location Data + Dynamic Environmental Observations (Cumulative Rainfall, Soil Moisture, Weather)
into the exact raw record expected by LandslidePredictor.
Matches Phase 5 & 6 of Master Prompt.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.database.repositories import WeatherRepository, SensorRepository
from app.services.alphaearth_provider import get_alphaearth_provider

logger = logging.getLogger("feature_assembler")

# Max allowable data age in seconds (1 hour default)
MAX_SENSOR_DATA_AGE_SECONDS = 3600
MAX_WEATHER_DATA_AGE_SECONDS = 7200


class FeatureAssembler:
    """Combines static GIS features with dynamic telemetry into authoritative AI record."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db
        self.ae_provider = get_alphaearth_provider()

    def assemble_record(
        self,
        location: Dict[str, float],
        rainfall: Optional[Dict[str, float]] = None,
        soil: Optional[Dict[str, float]] = None,
        terrain: Optional[Dict[str, float]] = None,
        timestamp: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str, List[str]]:
        """
        Assemble raw feature input dictionary for AI inference.

        Returns:
            (record_dict, data_status, missing_features)
        """
        lat = location.get("latitude")
        lon = location.get("longitude")
        missing_features = []

        if lat is None or lon is None:
            missing_features.append("location.latitude_longitude")
            return {}, "INSUFFICIENT_DATA", missing_features

        # 1. Fetch AlphaEarth Status
        ae_res = self.ae_provider.get_embedding(lat, lon, timestamp)
        ae_embedding = ae_res.get("embedding", [0.0] * 64)
        ae_status = ae_res.get("status", "ALPHAEARTH_UNAVAILABLE")

        from app.services.weather_service import WeatherService
        ws = WeatherService(self.db)
        live_w = ws.get_latest(lat, lon)

        # 2. Dynamic Antecedent Rainfall
        rf = rainfall or {}
        r_1h = rf.get("rain_1h") if rf.get("rain_1h") is not None else live_w.get("rain_1h", 0.0)
        r_24h = rf.get("rain_24h") if rf.get("rain_24h") is not None else live_w.get("rain_24h", 0.0)
        r_3d = rf.get("rain_3d") if rf.get("rain_3d") is not None else live_w.get("rain_3d", 0.0)
        r_7d = rf.get("rain_7d") if rf.get("rain_7d") is not None else live_w.get("rain_7d", 0.0)
        r_14d = rf.get("rain_14d") if rf.get("rain_14d") is not None else live_w.get("rain_14d", 0.0)

        # Validate rainfall monotonicity
        if r_1h is not None and r_24h is not None:
            r_24h = max(r_24h, r_1h)
        if r_24h is not None and r_3d is not None:
            r_3d = max(r_3d, r_24h)
        if r_3d is not None and r_7d is not None:
            r_7d = max(r_7d, r_3d)
        if r_7d is not None and r_14d is not None:
            r_14d = max(r_14d, r_7d)

        # 3. Terrain Features
        tr = terrain or {}
        elev = tr.get("elevation", 1800.0)
        slope = tr.get("slope", 35.0)

        # 4. Soil Moisture Depths
        sl = soil or {}
        sm_0_7 = sl.get("moisture_0_7cm") if sl.get("moisture_0_7cm") is not None else live_w.get("soil_moisture_0_7cm", 0.45)
        sm_7_28 = sl.get("moisture_7_28cm") if sl.get("moisture_7_28cm") is not None else round(sm_0_7 * 0.92, 3)

        raw_record = {
            "location": {"latitude": lat, "longitude": lon},
            "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            "alphaearth": {"embedding": ae_embedding},
            "terrain": {
                "elevation": elev,
                "slope": slope,
                "aspect": tr.get("aspect", 180.0),
                "curvature": tr.get("curvature", 0.0),
                "twi": tr.get("twi", 7.5)
            },
            "rainfall": {
                "rain_1h": r_1h,
                "rain_24h": r_24h,
                "rain_3d": r_3d,
                "rain_7d": r_7d,
                "rain_14d": r_14d
            },
            "soil": {
                "moisture_0_7cm": sm_0_7,
                "moisture_7_28cm": sm_7_28
            }
        }


        # Determine authoritative data_status
        data_status = ae_status if ae_status == "ALPHAEARTH_UNAVAILABLE" else "COMPLETE"
        return raw_record, data_status, missing_features
