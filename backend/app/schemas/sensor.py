"""Pydantic V2 Schemas for IoT Sensor Ingestion."""
from typing import Optional
from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):
    sensor_id: str = Field(..., example="ESP32_001")
    latitude: Optional[float] = Field(default=26.15, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=91.75, ge=-180.0, le=180.0)
    rainfall_mm: Optional[float] = Field(default=0.0, ge=0.0)
    soil_moisture: Optional[float] = Field(default=0.40, ge=0.0, le=1.0)
    temperature: Optional[float] = Field(default=25.0)
    humidity: Optional[float] = Field(default=85.0, ge=0.0, le=100.0)
    recorded_at: Optional[str] = None


class SensorResponse(BaseModel):
    id: int
    sensor_id: str
    name: Optional[str]
    latitude: float
    longitude: float
    sensor_type: str
    is_active: bool


class SensorTelemetryResponse(BaseModel):
    sensor_id: str
    location_id: Optional[int] = None
    latitude: float
    longitude: float
    sensor_type: Optional[str] = "rain_gauge"
    status: str  # ONLINE, STALE, NO_DATA
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    soil_moisture: Optional[float] = None
    rainfall_mm: Optional[float] = None
    recorded_at: Optional[str] = None

