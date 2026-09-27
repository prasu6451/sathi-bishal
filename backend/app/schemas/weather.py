"""Pydantic V2 Schemas for Weather Ingestion."""
from typing import Optional
from pydantic import BaseModel, Field


class WeatherObservationCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    rain_1h: float = Field(default=0.0, ge=0.0)
    rain_24h: float = Field(default=0.0, ge=0.0)
    rain_3d: float = Field(default=0.0, ge=0.0)
    rain_7d: float = Field(default=0.0, ge=0.0)
    rain_14d: float = Field(default=0.0, ge=0.0)
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    observed_at: Optional[str] = None


class WeatherObservationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    rain_1h: float
    rain_24h: float
    rain_3d: float
    rain_7d: float
    rain_14d: float
    observed_at: str
