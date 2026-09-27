"""Weather Ingestion API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repositories import WeatherRepository
from app.schemas.weather import WeatherObservationCreate, WeatherObservationResponse

router = APIRouter()


@router.post("/observations", response_model=WeatherObservationResponse, status_code=status.HTTP_201_CREATED)
def create_weather_observation(obs: WeatherObservationCreate, db: Session = Depends(get_db)):
    """Ingest weather observation and save to MySQL."""
    repo = WeatherRepository(db)
    db_obs = repo.create_observation(obs.model_dump())
    return WeatherObservationResponse(
        id=db_obs.id,
        latitude=db_obs.latitude,
        longitude=db_obs.longitude,
        rain_1h=db_obs.rain_1h,
        rain_24h=db_obs.rain_24h,
        rain_3d=db_obs.rain_3d,
        rain_7d=db_obs.rain_7d,
        rain_14d=db_obs.rain_14d,
        observed_at=db_obs.observed_at.isoformat()
    )


@router.get("/latest", response_model=WeatherObservationResponse)
def get_latest_weather(latitude: float = 26.15, longitude: float = 91.75, db: Session = Depends(get_db)):
    """Get latest weather observation near location."""
    repo = WeatherRepository(db)
    db_obs = repo.get_latest_near(latitude, longitude)
    if not db_obs:
        raise HTTPException(status_code=404, detail="No weather observations found.")
    return WeatherObservationResponse(
        id=db_obs.id,
        latitude=db_obs.latitude,
        longitude=db_obs.longitude,
        rain_1h=db_obs.rain_1h,
        rain_24h=db_obs.rain_24h,
        rain_3d=db_obs.rain_3d,
        rain_7d=db_obs.rain_7d,
        rain_14d=db_obs.rain_14d,
        observed_at=db_obs.observed_at.isoformat()
    )
