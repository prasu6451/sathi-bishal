"""Schemas package."""
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.schemas.sensor import SensorReadingCreate, SensorResponse
from app.schemas.report import CitizenReportCreate, CitizenReportResponse, RiskMapResponse
from app.schemas.weather import WeatherObservationCreate, WeatherObservationResponse

__all__ = [
    "PredictionRequest",
    "PredictionResponse",
    "SensorReadingCreate",
    "SensorResponse",
    "CitizenReportCreate",
    "CitizenReportResponse",
    "RiskMapResponse",
    "WeatherObservationCreate",
    "WeatherObservationResponse"
]
