"""
Development-Only Real-Time Simulation Demo Script.
Demonstrates location registration, IoT sensor ingestion, weather observations,
feature assembly, AI inference execution, database persistence, and WebSocket updates.
Matches Phase 35 of Master Prompt.
"""

import sys
import json
import logging
from pathlib import Path

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.connection import SessionLocal, init_db
from app.database.repositories import LocationRepository, SensorRepository, WeatherRepository, RiskPredictionRepository
from app.services.feature_assembler import FeatureAssembler
from app.services.ai_predictor import ai_predictor_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("demo_realtime")


def run_demo():
    logger.info("Initializing SATHI Real-Time AI Simulation Demo...")
    init_db()
    ai_predictor_service.load_model()

    if not ai_predictor_service.is_loaded:
        logger.error("AI Predictor engine could not be preloaded. Demo aborted.")
        return

    db = SessionLocal()
    try:
        # STEP 1: Register Monitored Location
        loc_repo = LocationRepository(db)
        location = loc_repo.create(name="Shillong Steep Ridge (Demo)", latitude=25.55, longitude=91.90)
        logger.info(f"STEP 1: Registered Location #{location.id}: {location.name} ({location.latitude}, {location.longitude})")

        # STEP 2: Register IoT Sensor & Ingest Readings
        sensor_repo = SensorRepository(db)
        sensor = sensor_repo.create_sensor("DEMO_ESP32_SHILLONG", "Shillong Ridge Rain Gauge", 25.55, 91.90)
        reading = sensor_repo.create_reading("DEMO_ESP32_SHILLONG", rainfall_mm=38.5, soil_moisture=0.58, temp=24.0, humidity=92.0)
        logger.info(f"STEP 2: Ingested IoT Reading #{reading.id}: Rain={reading.rainfall_mm}mm, Soil={reading.soil_moisture}")

        # STEP 3: Weather Observation Ingestion
        weather_repo = WeatherRepository(db)
        obs = weather_repo.create_observation({
            "latitude": 25.55,
            "longitude": 91.90,
            "rain_1h": 38.5,
            "rain_24h": 145.0,
            "rain_3d": 260.0,
            "rain_7d": 410.0,
            "rain_14d": 620.0,
            "temperature": 24.0,
            "soil_moisture": 0.58
        })
        logger.info(f"STEP 3: Ingested Weather Observation #{obs.id}: 24h Rain={obs.rain_24h}mm, 14d Rain={obs.rain_14d}mm")

        # STEP 4: Feature Assembly & Validation
        assembler = FeatureAssembler(db=db)
        raw_record, data_status, missing = assembler.assemble_record(
            location={"latitude": 25.55, "longitude": 91.90},
            rainfall={"rain_1h": obs.rain_1h, "rain_24h": obs.rain_24h, "rain_3d": obs.rain_3d, "rain_7d": obs.rain_7d, "rain_14d": obs.rain_14d},
            soil={"moisture_0_7cm": 0.58, "moisture_7_28cm": 0.52},
            terrain={"elevation": 1950.0, "slope": 48.2, "twi": 9.8}
        )
        logger.info(f"STEP 4: Assembled Feature Record. Data Status = '{data_status}'")

        # STEP 5: AI Model Inference
        pred_res = ai_predictor_service.predict(raw_record)
        logger.info(f"STEP 5: AI Model Inference Result: Prob={pred_res['landslide_probability']}, Score={pred_res['risk_score']}, Level={pred_res['risk_level']}")

        # STEP 6: Save Prediction in MySQL
        risk_repo = RiskPredictionRepository(db)
        db_pred = risk_repo.create({
            "location_id": location.id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "risk_probability": pred_res["landslide_probability"],
            "risk_score": pred_res["risk_score"],
            "risk_level": pred_res["risk_level"],
            "data_status": data_status,
            "model_version": pred_res["model_version"]
        })
        logger.info(f"STEP 6: Stored Prediction Record #{db_pred.id} in Database.")
        logger.info("Demo Completed Successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    run_demo()
