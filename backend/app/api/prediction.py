"""
Prediction REST API Endpoint (`POST /api/v1/predictions/predict`).
Matches Section 10 of Master Prompt.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import get_prediction_service, PredictionService
from app.database.connection import get_db
from app.database.repositories import RiskPredictionRepository
from datetime import datetime, timezone

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def predict_landslide_risk(
    request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
    db: Session = Depends(get_db)
) -> PredictionResponse:
    """
    Predict landslide risk probability and score using trained XGBoost model.
    Matches exact schema from Section 10 of Master Prompt.
    """
    if not prediction_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI Prediction service unavailable: {prediction_service.load_error}"
        )

    # Format input payload for feature builder
    record_dict = {
        "latitude": request.latitude,
        "longitude": request.longitude,
        "rainfall": {
            "rain_1h": request.rain_1h or 0.0,
            "rain_24h": request.rain_24h or 0.0,
            "rain_3d": request.rain_3d or 0.0,
            "rain_7d": request.rain_7d or 0.0,
            "rain_14d": request.rain_14d or 0.0
        },
        "soil": {
            "moisture_0_7cm": request.soil_moisture or 0.35,
            "moisture_7_28cm": request.soil_moisture or 0.35
        },
        "terrain": {
            "elevation": request.elevation or 1200.0,
            "slope": request.slope or 30.0,
            "aspect": request.aspect or 180.0,
            "twi": request.twi or 6.5
        }
    }

    if request.alphaearth_embedding:
        record_dict["alphaearth"] = {"embedding": request.alphaearth_embedding}

    try:
        res = prediction_service.predict(record_dict)

        # Store prediction result in MySQL
        now_dt = datetime.now(timezone.utc)
        repo = RiskPredictionRepository(db)
        repo.create({
            "latitude": request.latitude,
            "longitude": request.longitude,
            "risk_probability": res["risk_probability"],
            "risk_score": res["risk_score"],
            "risk_level": res["risk_level"],
            "model_version": res["model_version"],
            "prediction_timestamp": now_dt
        })

        return PredictionResponse(
            latitude=res["latitude"],
            longitude=res["longitude"],
            risk_probability=res["risk_probability"],
            risk_score=res["risk_score"],
            risk_level=res["risk_level"],
            model_version=res["model_version"],
            timestamp=now_dt.isoformat()
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing AI prediction: {str(err)}"
        )
