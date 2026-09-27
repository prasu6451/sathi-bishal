"""
Weather REST Endpoints matching Section 21 of Master Prompt.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.weather import WeatherObservationCreate, WeatherObservationResponse
from app.services.weather_service import WeatherService

router = APIRouter()


@router.post("/observations", response_model=WeatherObservationResponse, status_code=status.HTTP_201_CREATED)
async def log_weather_observation(payload: WeatherObservationCreate, db: Session = Depends(get_db)):
    """Fetch external weather or manually post weather observations."""
    service = WeatherService(db)
    res = await service.fetch_and_store_weather(payload.latitude, payload.longitude)
    if not res:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="External weather service unavailable")
    return res


@router.get("", response_model=WeatherObservationResponse)
async def get_current_weather(latitude: float, longitude: float, db: Session = Depends(get_db)):
    """Retrieve weather data for coordinates."""
    service = WeatherService(db)
    res = await service.fetch_and_store_weather(latitude, longitude)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No weather data available")
    return res
