"""API Router package."""
from fastapi import APIRouter
from app.api.v1.endpoints import predictions, sensors, reports, weather, risk, zones

api_router = APIRouter()

api_router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
api_router.include_router(reports.router, prefix="/reports", tags=["Citizen Reports"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Management & Map"])
api_router.include_router(zones.router, tags=["Zones"])
