"""
Sensor REST Endpoints matching Section 16 & 17 of Master Prompt.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.sensor import (
    SensorCreate,
    SensorResponse,
    SensorReadingCreate,
    SensorReadingResponse
)
from app.services.sensor_service import SensorService

router = APIRouter()


@router.post("", response_model=SensorResponse, status_code=status.HTTP_201_CREATED)
def register_sensor(payload: SensorCreate, db: Session = Depends(get_db)) -> SensorResponse:
    """Register a new IoT sensor device."""
    service = SensorService(db)
    return service.register_sensor(payload.model_dump())


@router.get("", response_model=List[SensorResponse])
def get_sensors(limit: int = 100, db: Session = Depends(get_db)) -> List[SensorResponse]:
    """Retrieve all registered IoT sensors."""
    service = SensorService(db)
    return service.get_sensors(limit=limit)


@router.get("/{sensor_id}", response_model=SensorResponse)
def get_sensor(sensor_id: str, db: Session = Depends(get_db)) -> SensorResponse:
    """Retrieve sensor by unique sensor_id."""
    service = SensorService(db)
    sensor = service.get_sensor_by_id(sensor_id)
    if not sensor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Sensor '{sensor_id}' not found")
    return sensor


@router.post("/readings", status_code=status.HTTP_201_CREATED)
async def ingest_sensor_reading(payload: SensorReadingCreate, db: Session = Depends(get_db)):
    """
    Ingest live IoT sensor reading, trigger AI inference, save to MySQL, and broadcast via WebSockets.
    """
    service = SensorService(db)
    result = await service.ingest_reading(payload.model_dump())
    return {
        "status": "success",
        "sensor_reading_id": result["sensor_reading_id"],
        "prediction": result["prediction"]
    }


@router.get("/{sensor_id}/readings", response_model=List[SensorReadingResponse])
def get_sensor_readings(sensor_id: str, limit: int = 50, db: Session = Depends(get_db)) -> List[SensorReadingResponse]:
    """Get historical readings for a specific sensor."""
    service = SensorService(db)
    return service.get_sensor_readings(sensor_id, limit=limit)
