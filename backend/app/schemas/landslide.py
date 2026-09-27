"""
Pydantic schemas for Landslide risk inference requests, responses, and assessment logs.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class LocationInput(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, json_schema_extra={"example": 30.3165})
    longitude: float = Field(..., ge=-180.0, le=180.0, json_schema_extra={"example": 78.0322})


class TerrainInput(BaseModel):
    elevation: Optional[float] = Field(None, json_schema_extra={"example": 1820.4})
    slope: Optional[float] = Field(None, ge=0.0, le=90.0, json_schema_extra={"example": 34.7})
    aspect: Optional[float] = Field(None, json_schema_extra={"example": 210.3})
    curvature: Optional[float] = Field(None, json_schema_extra={"example": 0.18})
    twi: Optional[float] = Field(None, json_schema_extra={"example": 7.4})


class RainfallInput(BaseModel):
    rain_1h: Optional[float] = Field(None, ge=0.0, json_schema_extra={"example": 18.2})
    rain_24h: Optional[float] = Field(None, ge=0.0, json_schema_extra={"example": 84.5})
    rain_3d: Optional[float] = Field(None, ge=0.0, json_schema_extra={"example": 162.2})
    rain_7d: Optional[float] = Field(None, ge=0.0, json_schema_extra={"example": 280.1})
    rain_14d: Optional[float] = Field(None, ge=0.0, json_schema_extra={"example": 421.3})


class SoilInput(BaseModel):
    moisture_0_7cm: Optional[float] = Field(None, ge=0.0, le=1.0, json_schema_extra={"example": 0.42})
    moisture_7_28cm: Optional[float] = Field(None, ge=0.0, le=1.0, json_schema_extra={"example": 0.38})


class AlphaEarthInput(BaseModel):
    embedding: Optional[List[float]] = Field(None, description="64-dimensional AlphaEarth embedding vector")


class LandslidePredictionRequest(BaseModel):
    id: Optional[str] = Field(None, json_schema_extra={"example": "req_0001"})
    location: LocationInput
    timestamp: Optional[str] = Field(None, json_schema_extra={"example": "2025-08-20T12:00:00Z"})
    alphaearth: Optional[AlphaEarthInput] = None
    terrain: Optional[TerrainInput] = None
    rainfall: Optional[RainfallInput] = None
    soil: Optional[SoilInput] = None
    satellite: Optional[Dict[str, Any]] = None
    geology: Optional[Dict[str, Any]] = None
    infrastructure: Optional[Dict[str, Any]] = None
    population: Optional[Dict[str, Any]] = None
    land_use: Optional[Dict[str, Any]] = None
    historical: Optional[Dict[str, Any]] = None
    iot: Optional[Dict[str, Any]] = None
    citizen_report: Optional[Dict[str, Any]] = None


class LandslidePredictionResponse(BaseModel):
    assessment_id: str = Field(..., json_schema_extra={"example": "eval_8a12f"})
    latitude: float = Field(..., json_schema_extra={"example": 30.3165})
    longitude: float = Field(..., json_schema_extra={"example": 78.0322})
    landslide_probability: float = Field(..., json_schema_extra={"example": 0.8321})
    risk_score: int = Field(..., json_schema_extra={"example": 83})
    risk_level: str = Field(..., json_schema_extra={"example": "CRITICAL"})
    timestamp: Optional[str] = Field(None, json_schema_extra={"example": "2025-08-20T12:00:00Z"})
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class AssessmentLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assessment_id: str
    latitude: float
    longitude: float
    landslide_probability: float
    risk_score: int
    risk_level: str
    timestamp: Optional[str]
    created_at: datetime
