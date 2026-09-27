"""Risk History & Map API Endpoints."""
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repositories import RiskPredictionRepository
from app.schemas.prediction import PredictionResponse
from app.schemas.report import RiskMapResponse

router = APIRouter()


@router.get("/latest", response_model=List[PredictionResponse])
def get_latest_risk_predictions(db: Session = Depends(get_db)):
    """Fetch latest risk prediction for each monitored location."""
    repo = RiskPredictionRepository(db)
    preds = repo.get_latest_predictions_all_locations()
    return [
        PredictionResponse(
            prediction_id=p.id,
            latitude=p.latitude,
            longitude=p.longitude,
            landslide_probability=p.landslide_probability,
            risk_score=p.risk_score,
            risk_level=p.risk_level,
            model_version=p.model_version,
            timestamp=p.prediction_timestamp.isoformat()
        )
        for p in preds
    ]


@router.get("/history", response_model=List[PredictionResponse])
def get_risk_prediction_history(limit: int = 100, db: Session = Depends(get_db)):
    """Fetch risk prediction history."""
    repo = RiskPredictionRepository(db)
    preds = repo.get_history(limit=limit)
    return [
        PredictionResponse(
            prediction_id=p.id,
            latitude=p.latitude,
            longitude=p.longitude,
            landslide_probability=p.landslide_probability,
            risk_score=p.risk_score,
            risk_level=p.risk_level,
            model_version=p.model_version,
            timestamp=p.prediction_timestamp.isoformat()
        )
        for p in preds
    ]


@router.get("/map", response_model=RiskMapResponse)
def get_risk_map(db: Session = Depends(get_db)):
    """Fetch spatial risk map payload for frontend renderer."""
    repo = RiskPredictionRepository(db)
    preds = repo.get_latest_predictions_all_locations()
    now_str = datetime.now(timezone.utc).isoformat()
    locations = [
        PredictionResponse(
            prediction_id=p.id,
            latitude=p.latitude,
            longitude=p.longitude,
            landslide_probability=p.landslide_probability,
            risk_score=p.risk_score,
            risk_level=p.risk_level,
            model_version=p.model_version,
            timestamp=p.prediction_timestamp.isoformat()
        )
        for p in preds
    ]
    return RiskMapResponse(timestamp=now_str, locations=locations)
