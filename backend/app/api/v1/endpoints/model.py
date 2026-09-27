"""Model Status API Endpoint: GET /api/v1/model/status."""
from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.services.ai_predictor import get_ai_predictor, AIPredictionService

from app.services.alphaearth_provider import get_alphaearth_provider

router = APIRouter()


@router.get("/status", response_model=Dict[str, Any])
def get_model_status(ai_service: AIPredictionService = Depends(get_ai_predictor)):
    """Get active AI model version, schema feature count, threshold, and AlphaEarth status."""
    ae_status = get_alphaearth_provider().get_embedding(26.15, 91.75).get("alphaearth_status", "VERIFIED")

    if not ai_service.is_loaded or ai_service.predictor is None:
        return {
            "model_version": "unknown",
            "loaded": False,
            "feature_count": 109,
            "alphaearth_status": ae_status,
            "threshold": 0.50
        }

    predictor = ai_service.predictor
    feature_count = predictor.schema.feature_count if predictor.schema else 109

    return {
        "model_version": predictor.model_version,
        "loaded": True,
        "feature_count": feature_count,
        "alphaearth_status": ae_status,
        "threshold": 0.50,
        "prediction_horizon_hours": 24
    }

