"""Health check response Pydantic schema."""

from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    database_status: str = Field(..., json_schema_extra={"example": "connected"})
    ai_model_loaded: bool = Field(..., json_schema_extra={"example": True})
    ai_model_path: str = Field(..., json_schema_extra={"example": "saved_models/landslide_xgboost.json"})
    details: Dict[str, Any] = Field(default_factory=dict)
