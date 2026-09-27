"""
Risk Management REST Endpoints matching Section 19 & 20 of Master Prompt.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.prediction import PredictionResponse
from app.services.risk_service import RiskService

router = APIRouter()


@router.get("/latest", response_model=List[PredictionResponse])
def get_latest_risk_predictions(limit: int = 50, db: Session = Depends(get_db)) -> List[PredictionResponse]:
    """Retrieve latest risk predictions across all locations."""
    service = RiskService(db)
    preds = service.get_latest_risk_predictions(limit=limit)
    return [
        PredictionResponse(
            latitude=p.latitude,
            longitude=p.longitude,
            risk_probability=p.risk_probability,
            risk_score=p.risk_score,
            risk_level=p.risk_level,
            model_version=p.model_version,
            timestamp=p.prediction_timestamp.isoformat()
        )
        for p in preds
    ]


@router.get("/history", response_model=List[PredictionResponse])
def get_risk_history(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[PredictionResponse]:
    """Get historical risk predictions for specific location coordinates."""
    service = RiskService(db)
    preds = service.get_risk_history(
        latitude=latitude,
        longitude=longitude,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    return [
        PredictionResponse(
            latitude=p.latitude,
            longitude=p.longitude,
            risk_probability=p.risk_probability,
            risk_score=p.risk_score,
            risk_level=p.risk_level,
            model_version=p.model_version,
            timestamp=p.prediction_timestamp.isoformat()
        )
        for p in preds
    ]


@router.get("/map", status_code=status.HTTP_200_OK)
def get_risk_map(db: Session = Depends(get_db)):
    """
    Get Risk Map payload formatted for frontend map visualization (Section 20).
    """
    service = RiskService(db)
    return service.get_risk_map_data()
