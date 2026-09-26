"""
Asyncio Background Risk Monitor Worker executing periodic risk evaluation loop across North-East monitored locations.
Matches Section 11, 15, 36 of Master Prompt.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.database.connection import SessionLocal
from app.database.repositories import RiskPredictionRepository, WeatherRepository, SensorRepository
from app.services.prediction_service import get_prediction_service
from app.websocket.manager import manager
from app.schemas.prediction import PredictionResponse

logger = logging.getLogger(__name__)

# Monitored spatial locations covering North-East India
DEFAULT_MONITORED_LOCATIONS = [
    {"name": "Guwahati Ridge (Assam)", "latitude": 26.15, "longitude": 91.75, "slope": 44.5, "elevation": 2100.0},
    {"name": "Shillong Plateau (Meghalaya)", "latitude": 25.55, "longitude": 91.90, "slope": 48.2, "elevation": 1950.0},
    {"name": "Itanagar Hills (Arunachal Pradesh)", "latitude": 27.08, "longitude": 93.65, "slope": 38.7, "elevation": 1820.0},
    {"name": "Gangtok Gorge (Sikkim)", "latitude": 27.33, "longitude": 88.62, "slope": 51.0, "elevation": 2200.0},
    {"name": "Ukhrul Slopes (Manipur)", "latitude": 24.82, "longitude": 93.95, "slope": 28.4, "elevation": 1450.0},
    {"name": "Aizawl Ridge (Mizoram)", "latitude": 23.73, "longitude": 92.72, "slope": 36.5, "elevation": 1650.0},
    {"name": "Kohima Ridge (Nagaland)", "latitude": 25.65, "longitude": 94.10, "slope": 37.8, "elevation": 1780.0},
    {"name": "Jampui Hills (Tripura)", "latitude": 23.83, "longitude": 91.28, "slope": 8.2, "elevation": 650.0}
]


class RiskMonitorWorker:
    """Periodic background worker executing risk evaluation and broadcasting live updates."""

    def __init__(self, interval_seconds: Optional[int] = None) -> None:
        self.interval_seconds = interval_seconds or settings.RISK_UPDATE_INTERVAL_SECONDS
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.prediction_service = get_prediction_service()

    def start(self) -> None:
        """Start the background monitoring loop task."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info(f"RiskMonitorWorker started with update interval: {self.interval_seconds}s")

    async def stop(self) -> None:
        """Stop the worker cleanly."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("RiskMonitorWorker stopped cleanly.")

    async def _run_loop(self) -> None:
        """Main periodic loop execution."""
        while self._running:
            try:
                await self.evaluate_and_broadcast()
            except Exception as err:
                logger.error(f"Error in RiskMonitorWorker evaluation loop: {err}")

            try:
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break

    async def evaluate_and_broadcast(self) -> None:
        """
        Execute risk evaluation across monitored North-East locations, store in DB, and broadcast via WebSockets.
        """
        if not self.prediction_service.is_loaded:
            logger.warning("PredictionService is not loaded. Risk monitor skipping evaluation cycle.")
            return

        db = SessionLocal()
        batch_updates: List[Dict[str, Any]] = []

        try:
            risk_repo = RiskPredictionRepository(db)
            weather_repo = WeatherRepository(db)
            sensor_repo = SensorRepository(db)

            for loc in DEFAULT_MONITORED_LOCATIONS:
                lat = loc["latitude"]
                lon = loc["longitude"]

                # Check if sensor or weather observation exists
                weather_obs = weather_repo.get_latest_near(lat, lon)
                
                # Check sensor cumulative rainfall
                sensors = sensor_repo.get_active_sensors_with_latest_readings()
                matched_sensor = next((s for s in sensors if abs(s["latitude"] - lat) < 0.2 and abs(s["longitude"] - lon) < 0.2), None)

                if matched_sensor and matched_sensor.get("sensor_id"):
                    cum_rain = sensor_repo.get_cumulative_rainfall_windows(matched_sensor["sensor_id"])
                    r_1h = cum_rain["rain_1h"]
                    r_24h = cum_rain["rain_24h"]
                    r_3d = cum_rain["rain_3d"]
                    r_7d = cum_rain["rain_7d"]
                    r_14d = cum_rain["rain_14d"]
                    soil_m = matched_sensor.get("soil_moisture") or 0.40
                elif weather_obs:
                    r_1h = weather_obs.rain_1h
                    r_24h = weather_obs.rain_24h
                    r_3d = weather_obs.rain_3d
                    r_7d = weather_obs.rain_7d
                    r_14d = weather_obs.rain_14d
                    soil_m = weather_obs.soil_moisture or 0.40
                else:
                    r_1h, r_24h, r_3d, r_7d, r_14d = 0.0, 0.0, 0.0, 0.0, 0.0
                    soil_m = 0.35

                feature_payload = {
                    "latitude": lat,
                    "longitude": lon,
                    "rainfall": {
                        "rain_1h": r_1h,
                        "rain_24h": r_24h,
                        "rain_3d": r_3d,
                        "rain_7d": r_7d,
                        "rain_14d": r_14d
                    },
                    "soil": {"moisture_0_7cm": soil_m, "moisture_7_28cm": round(soil_m * 0.95, 4)},
                    "terrain": {"elevation": loc["elevation"], "slope": loc["slope"], "twi": 7.4}
                }

                # Run AI prediction
                res = self.prediction_service.predict(feature_payload)
                now_dt = datetime.now(timezone.utc)

                # Store risk prediction in database
                risk_repo.create({
                    "latitude": lat,
                    "longitude": lon,
                    "risk_probability": res["landslide_probability"],
                    "risk_score": res["risk_score"],
                    "risk_level": res["risk_level"],
                    "model_version": res["model_version"],
                    "prediction_timestamp": now_dt
                })

                batch_updates.append(
                    PredictionResponse(
                        latitude=lat,
                        longitude=lon,
                        landslide_probability=res["landslide_probability"],
                        risk_score=res["risk_score"],
                        risk_level=res["risk_level"],
                        model_version=res["model_version"],
                        timestamp=now_dt.isoformat()
                    ).model_dump()
                )

            # Broadcast batch risk updates to all connected WebSockets
            if batch_updates and manager.client_count > 0:
                ws_message = {
                    "type": "risk_update",
                    "data": batch_updates
                }
                await manager.broadcast(ws_message)
                logger.info(f"Broadcasted periodic risk update to {manager.client_count} WebSocket clients.")

        except Exception as err:
            logger.error(f"Error during risk evaluation & broadcast: {err}")
        finally:
            db.close()


risk_monitor_worker = RiskMonitorWorker()
