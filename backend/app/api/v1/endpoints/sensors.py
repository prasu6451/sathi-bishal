"""Sensors API Endpoint: POST /api/v1/sensors/readings."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repositories import SensorRepository
from app.schemas.sensor import SensorReadingCreate, SensorResponse, SensorTelemetryResponse
from app.services.prediction_service import get_prediction_service, PredictionService
from app.schemas.prediction import PredictionRequest, LocationSchema, RainfallSchema, SoilSchema

router = APIRouter()


@router.get("", response_model=List[SensorTelemetryResponse])
def get_active_sensors(db: Session = Depends(get_db)):
    """
    GET /api/v1/sensors: Return all active IoT sensors with latest readings and calculated status.
    Matches Phase 2, 3, 4 of Master Prompt.
    """
    repo = SensorRepository(db)
    return repo.get_active_sensors_with_latest_readings()


@router.post("/readings", status_code=status.HTTP_201_CREATED)
async def ingest_sensor_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db),
    prediction_service: PredictionService = Depends(get_prediction_service)
):
    """
    Ingest IoT Sensor reading, validate telemetry ranges, compute cumulative rainfall windows from history,
    run AI inference, persist to MySQL, and broadcast WebSocket risk_update.
    Matches Phase 7, 8, 9, 10 of Master Prompt.
    """
    # 1. Physical validation of telemetry ranges (Phase 30 & 31)
    if reading.temperature is not None and not (-50.0 <= reading.temperature <= 60.0):
        raise HTTPException(status_code=400, detail="Invalid temperature value. Must be between -50°C and +60°C.")
    if reading.humidity is not None and not (0.0 <= reading.humidity <= 100.0):
        raise HTTPException(status_code=400, detail="Invalid humidity value. Must be between 0% and 100%.")
    if reading.rainfall_mm is not None and reading.rainfall_mm < 0.0:
        raise HTTPException(status_code=400, detail="Invalid rainfall value. Must be non-negative.")
    
    soil_m = reading.soil_moisture if reading.soil_moisture is not None else 0.40
    if soil_m > 1.0:  # If passed as percentage (e.g. 45%), convert to ratio (0.45)
        soil_m = soil_m / 100.0
    if not (0.0 <= soil_m <= 1.0):
        raise HTTPException(status_code=400, detail="Invalid soil moisture value. Must be between 0.0 and 1.0 (or 0% and 100%).")

    repo = SensorRepository(db)
    sensor = repo.get_by_sensor_id(reading.sensor_id)

    if not sensor:
        sensor = repo.create_sensor(
            sensor_id=reading.sensor_id,
            name=f"Sensor {reading.sensor_id}",
            lat=reading.latitude or 26.15,
            lon=reading.longitude or 91.75
        )

    db_reading = repo.create_reading(
        sensor_id=reading.sensor_id,
        rainfall_mm=reading.rainfall_mm or 0.0,
        soil_moisture=soil_m,
        temp=reading.temperature if reading.temperature is not None else 25.0,
        humidity=reading.humidity if reading.humidity is not None else 85.0
    )

    # 2. Calculate true antecedent cumulative rainfall from DB history (Phase 5)
    cum_rain = repo.get_cumulative_rainfall_windows(reading.sensor_id)

    # 3. Automatically trigger AI prediction update if AI model is loaded (Phase 10)
    prediction_resp = None
    if prediction_service.is_loaded:
        req = PredictionRequest(
            location=LocationSchema(latitude=sensor.latitude, longitude=sensor.longitude),
            rainfall=RainfallSchema(
                rain_1h=cum_rain["rain_1h"],
                rain_24h=cum_rain["rain_24h"],
                rain_3d=cum_rain["rain_3d"],
                rain_7d=cum_rain["rain_7d"],
                rain_14d=cum_rain["rain_14d"]
            ),
            soil=SoilSchema(
                moisture_0_7cm=soil_m,
                moisture_7_28cm=round(soil_m * 0.95, 4)  # Documented soil profile depth attenuation
            )
        )
        telemetry_dict = {
            "temperature": db_reading.temperature,
            "humidity": db_reading.humidity,
            "soil_moisture": db_reading.soil_moisture,
            "rainfall_mm": db_reading.rainfall_mm
        }
        prediction_resp = await prediction_service.execute_prediction(req, db, telemetry=telemetry_dict)

    return {
        "status": "success",
        "sensor_reading_id": db_reading.id,
        "prediction": prediction_resp
    }

