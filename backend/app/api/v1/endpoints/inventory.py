"""
Landslide Inventory REST API Endpoint.
Exposes 11,026 real-world geological survey landslide records from SIH26001_DATA.
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter, Query
from app.services.landslide_inventory_service import LandslideInventoryService

router = APIRouter()
inventory_service = LandslideInventoryService()


@router.get("/inventory/landslides", response_model=Dict[str, Any])
def get_landslide_inventory(
    state: Optional[str] = Query(None, description="Filter by North-East India state name (e.g. Assam, Meghalaya, Sikkim, Mizoram)"),
    district: Optional[str] = Query(None, description="Filter by District name"),
    movement_type: Optional[str] = Query(None, description="Filter by Movement Type (Slide, Fall, Flow, Debris)"),
    limit: int = Query(200, ge=1, le=2000, description="Max number of records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
) -> Dict[str, Any]:
    """Query 11,026 authoritative historical landslide records from SIH26001 dataset."""
    return inventory_service.query_inventory(
        state=state,
        district=district,
        movement_type=movement_type,
        limit=limit,
        offset=offset
    )


@router.get("/inventory/stats", response_model=Dict[str, Any])
def get_inventory_stats() -> Dict[str, Any]:
    """Get state-wise and movement-type statistical breakdown across all 11,026 records."""
    return inventory_service.get_summary_stats()


@router.get("/inventory/nearby")
def get_nearby_landslides(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    radius_km: float = Query(25.0, ge=1.0, le=200.0),
    limit: int = Query(50, ge=1, le=200)
):
    """Find historical landslide events near a specific GPS coordinate."""
    return inventory_service.get_nearby_incidents(
        lat=latitude,
        lon=longitude,
        radius_km=radius_km,
        limit=limit
    )
