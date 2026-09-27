"""
Landslide risk prediction and assessment log endpoints.
"""

import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import LandslideAssessment
from app.schemas.landslide import (
    LandslidePredictionRequest,
    LandslidePredictionResponse,
    AssessmentLogResponse
)
from app.services.ai_predictor import get_ai_predictor, AIPredictionService

router = APIRouter()


@router.post("/predict", response_model=LandslidePredictionResponse, status_code=status.HTTP_200_OK)
def predict_landslide_risk(
    payload: LandslidePredictionRequest,
    db: Session = Depends(get_db),
    ai_service: AIPredictionService = Depends(get_ai_predictor)
) -> LandslidePredictionResponse:
    """
    Accept environmental/geospatial payload, run XGBoost landslide risk prediction, and log assessment to DB.
    """
    if not ai_service.is_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI model prediction service is currently unavailable. Details: {ai_service.load_error}"
        )

    try:
        raw_dict = payload.model_dump()
        result = ai_service.predict(raw_dict)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Landslide risk inference failed: {err}"
        )

    assessment_id = f"eval_{uuid.uuid4().hex[:10]}"
    lat = payload.location.latitude
    lon = payload.location.longitude

    # Save to database log
    try:
        db_log = LandslideAssessment(
            assessment_id=assessment_id,
            latitude=lat,
            longitude=lon,
            timestamp=payload.timestamp,
            landslide_probability=result["landslide_probability"],
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            raw_input_json=json.dumps(raw_dict)
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
    except Exception as db_err:
        # Non-blocking log warning if DB write fails
        db.rollback()

    return LandslidePredictionResponse(
        assessment_id=assessment_id,
        latitude=lat,
        longitude=lon,
        landslide_probability=result["landslide_probability"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        timestamp=payload.timestamp
    )


@router.get("/predict/assessments", response_model=List[AssessmentLogResponse])
def list_assessments(
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[AssessmentLogResponse]:
    """Retrieve recent landslide risk assessment logs."""
    logs = (
        db.query(LandslideAssessment)
        .order_by(LandslideAssessment.created_at.desc())
        .limit(limit)
        .all()
    )
    return logs
