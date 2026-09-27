"""Sensor Service layer for IoT Data Handling."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.repositories import SensorRepository


class SensorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SensorRepository(db)

    def ingest_reading(self, data: Dict[str, Any]):
        return self.repo.create_reading(
            sensor_id=data["sensor_id"],
            rainfall_mm=data.get("rainfall_mm", 0.0),
            soil_moisture=data.get("soil_moisture", 0.40),
            temp=data.get("temperature", 25.0),
            humidity=data.get("humidity", 85.0),
            recorded_at=data.get("recorded_at")
        )
