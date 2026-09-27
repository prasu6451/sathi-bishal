"""
Pydantic v2 schemas for WebSocket live risk messages matching Section 14, 15, 34 of Master Prompt.
"""

from typing import Union, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.prediction import PredictionResponse


class WebSocketRiskMessage(BaseModel):
    type: str = Field("risk_update", json_schema_extra={"example": "risk_update"})
    data: PredictionResponse


class WebSocketBatchRiskMessage(BaseModel):
    type: str = Field("initial_risk_state", json_schema_extra={"example": "initial_risk_state"})
    data: List[PredictionResponse]
