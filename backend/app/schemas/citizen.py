"""
Pydantic schemas for citizen report filing and retrieval.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CitizenReportCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 30.3165})
    longitude: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 78.0322})
    reporter_name: Optional[str] = Field(None, json_schema_extra={"example": "Anonymous Citizen"})
    severity: int = Field(1, ge=1, le=3, description="1: Minor, 2: Moderate, 3: Severe/Blocking")
    description: Optional[str] = Field(None, json_schema_extra={"example": "Cracks observed near roadside slope after heavy rain."})


class CitizenReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_id: str
    latitude: float
    longitude: float
    reporter_name: Optional[str]
    severity: int
    description: Optional[str]
    status: str
    created_at: datetime
