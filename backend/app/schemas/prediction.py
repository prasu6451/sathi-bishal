"""Pydantic V2 Schemas for AI Prediction Input & Output."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class TerrainSchema(BaseModel):
    elevation: float = Field(default=1800.0)
    slope: float = Field(default=35.0, ge=0.0)
    aspect: float = Field(default=180.0, ge=0.0, le=360.0)
    curvature: float = Field(default=0.0)
    twi: float = Field(default=7.5, ge=0.0)


class RainfallSchema(BaseModel):
    rain_1h: float = Field(default=15.0, ge=0.0)
    rain_24h: float = Field(default=85.0, ge=0.0)
    rain_3d: float = Field(default=165.0, ge=0.0)
    rain_7d: float = Field(default=290.0, ge=0.0)
    rain_14d: float = Field(default=430.0, ge=0.0)


class SoilSchema(BaseModel):
    moisture_0_7cm: float = Field(default=0.45, ge=0.0, le=1.0)
    moisture_7_28cm: float = Field(default=0.41, ge=0.0, le=1.0)


class AlphaEarthSchema(BaseModel):
    embedding: List[float] = Field(default_factory=lambda: [0.0] * 64)


class PredictionRequest(BaseModel):
    location: LocationSchema
    timestamp: Optional[str] = None
    terrain: Optional[TerrainSchema] = Field(default_factory=TerrainSchema)
    rainfall: Optional[RainfallSchema] = Field(default_factory=RainfallSchema)
    soil: Optional[SoilSchema] = Field(default_factory=SoilSchema)
    alphaearth: Optional[AlphaEarthSchema] = Field(default_factory=AlphaEarthSchema)
    satellite: Optional[Dict[str, Any]] = None
    geology: Optional[Dict[str, Any]] = None
    infrastructure: Optional[Dict[str, Any]] = None
    population: Optional[Dict[str, Any]] = None
    historical: Optional[Dict[str, Any]] = None
    iot: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    prediction_id: Optional[int] = None
    latitude: float
    longitude: float
    landslide_probability: float
    risk_score: int
    risk_level: str  # LOW, MODERATE, HIGH, CRITICAL
    data_status: str = "ALPHAEARTH_UNAVAILABLE"
    model_version: str = "xgb-v1"
    timestamp: str
