"""Pydantic V2 Schemas for Citizen Reports & Risk Map."""
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.prediction import PredictionResponse


class CitizenReportCreate(BaseModel):
    latitude: Optional[float] = Field(default=26.1445, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=91.7362, ge=-180.0, le=180.0)
    severity: Optional[int] = Field(default=3, ge=1, le=5)
    disaster_type: Optional[str] = "landslide"
    risk_level: Optional[str] = "moderate"
    location_name: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class CitizenReportResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    severity: int
    disaster_type: Optional[str] = "landslide"
    risk_level: Optional[str] = "moderate"
    location_name: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    verification_status: Optional[str] = "PENDING"
    authority_notes: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None
    created_at: str


class CitizenReportVerify(BaseModel):
    verification_status: str
    authority_notes: Optional[str] = None
    verified_by: Optional[str] = "Admin Authority"


class RiskMapResponse(BaseModel):
    timestamp: str
    locations: List[PredictionResponse]

