"""Predictions API Endpoint: POST /api/v1/predictions/predict."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import get_prediction_service, PredictionService

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    req: PredictionRequest,
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Run AI inference for a geospatial location and save risk prediction to database.
    Broadcasts risk_update over WebSockets if active clients exist.
    """
    if not prediction_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Model Predictor is currently unavailable."
        )

    try:
        return await prediction_service.execute_prediction(req, db)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction failed: {err}"
        )
