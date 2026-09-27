"""
Health check endpoint reporting API status, database health, and AI model status.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.database.session import get_db
from app.schemas.health import HealthCheckResponse
from app.services.ai_predictor import get_ai_predictor, AIPredictionService

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
def health_check(
    db: Session = Depends(get_db),
    ai_service: AIPredictionService = Depends(get_ai_predictor)
) -> HealthCheckResponse:
    """Check API server, database connectivity, and AI model initialization state."""
    # Check DB
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as err:
        db_status = f"disconnected: {err}"

    return HealthCheckResponse(
        status="ok",
        version=settings.VERSION,
        database_status=db_status,
        ai_model_loaded=ai_service.is_loaded,
        ai_model_path=str(ai_service.model_dir),
        details={
            "load_error": ai_service.load_error
        }
    )
