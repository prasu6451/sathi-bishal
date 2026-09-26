"""
Landslide Inventory Service for loading, indexing, and serving authoritative
11,026 historical landslide records from SIH26001_DATA corpus.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("landslide_inventory_service")

# Path to authoritative 11,026 landslide inventory dataset
_base_dir = Path(__file__).resolve().parent.parent.parent.parent
INVENTORY_JSON_PATH = _base_dir / "SIH26001_DATA" / "01_landslide inventory" / "01_landslide_inventory_NE_8_states.json"
if not INVENTORY_JSON_PATH.exists():
    INVENTORY_JSON_PATH = Path("../SIH26001_DATA/01_landslide inventory/01_landslide_inventory_NE_8_states.json")


class LandslideInventoryService:
    """Provides high-performance spatial and attribute search over 11,026 real-world landslide records."""

    _cache_data: Optional[Dict[str, Any]] = None
    _records: List[Dict[str, Any]] = []

    def __init__(self) -> None:
        self._ensure_loaded()

    @classmethod
    def _ensure_loaded(cls) -> None:
        if cls._cache_data is not None:
            return

        if INVENTORY_JSON_PATH.exists():
            try:
                with open(INVENTORY_JSON_PATH, "r", encoding="utf-8") as f:
                    cls._cache_data = json.load(f)
                    cls._records = cls._cache_data.get("records", [])
                logger.info(f"Loaded {len(cls._records)} authoritative historical landslide records from SIH26001_DATA.")
            except Exception as err:
                logger.error(f"Failed to parse landslide inventory JSON: {err}")
                cls._records = []
        else:
            logger.warning(f"Landslide inventory JSON not found at {INVENTORY_JSON_PATH}")
            cls._records = []

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary breakdown of 11,026 historical landslide records by state and movement type."""
        state_counts = {}
        type_counts = {}
        material_counts = {}

        for rec in self._records:
            st = (rec.get("State") or "Unknown").title()
            mt = (rec.get("Movement_Type") or "Slide").title()
            mat = (rec.get("Material_Involved") or "Debris").title()

            state_counts[st] = state_counts.get(st, 0) + 1
            type_counts[mt] = type_counts.get(mt, 0) + 1
            material_counts[mat] = material_counts.get(mat, 0) + 1

        return {
            "total_records": len(self._records),
            "state_counts": state_counts,
            "movement_type_counts": type_counts,
            "material_counts": material_counts,
            "data_source": "SIH26001_DATA Authoritative 8-State Geological Survey Dataset"
        }

    def query_inventory(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        movement_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Filter inventory records by state, district, or movement type."""
        filtered = self._records

        if state:
            s_lower = state.strip().lower()
            filtered = [r for r in filtered if r.get("State", "").lower() == s_lower]

        if district:
            d_lower = district.strip().lower()
            filtered = [r for r in filtered if d_lower in r.get("District", "").lower()]

        if movement_type:
            m_lower = movement_type.strip().lower()
            filtered = [r for r in filtered if m_lower in r.get("Movement_Type", "").lower()]

        total_matching = len(filtered)
        paginated = filtered[offset : offset + limit]

        # Standardize coordinates
        output_records = []
        for r in paginated:
            output_records.append({
                "id": r.get("Slide_No") or f"SLIDE-{r.get('Sl.No.')}",
                "slide_name": r.get("Slide_Name") or "Unspecified Landslide Incident",
                "state": r.get("State"),
                "district": r.get("District"),
                "location_name": r.get("NH_SH_Location"),
                "latitude": r.get("Latitude"),
                "longitude": r.get("Longitude"),
                "material_involved": r.get("Material_Involved") or "Debris",
                "movement_type": r.get("Movement_Type") or "Slide",
                "history": r.get("History")
            })

        return {
            "total": total_matching,
            "limit": limit,
            "offset": offset,
            "records": output_records
        }

    def get_nearby_incidents(self, lat: float, lon: float, radius_km: float = 25.0, limit: int = 50) -> List[Dict[str, Any]]:
        """Find historical landslide incidents within a radius of (lat, lon)."""
        nearby = []
        # Approx 1 deg lat = 111 km
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / 95.0

        for r in self._records:
            r_lat = r.get("Latitude")
            r_lon = r.get("Longitude")
            if r_lat is None or r_lon is None:
                continue

            if abs(r_lat - lat) <= lat_delta and abs(r_lon - lon) <= lon_delta:
                dist_sq = (r_lat - lat) ** 2 + (r_lon - lon) ** 2
                nearby.append((dist_sq, r))

        nearby.sort(key=lambda x: x[0])
        results = []
        for _, r in nearby[:limit]:
            results.append({
                "id": r.get("Slide_No") or f"SLIDE-{r.get('Sl.No.')}",
                "slide_name": r.get("Slide_Name") or "Historical Incident",
                "state": r.get("State"),
                "district": r.get("District"),
                "latitude": r.get("Latitude"),
                "longitude": r.get("Longitude"),
                "material": r.get("Material_Involved"),
                "movement": r.get("Movement_Type")
            })

        return results
