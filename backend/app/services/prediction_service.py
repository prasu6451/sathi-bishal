"""
Prediction Service orchestrating REST Requests, Feature Assembly, Database Persistence,
and WebSocket Real-Time Risk Broadcasts.
Architectural Flow: API -> Service -> FeatureAssembler -> AI Predictor -> MySQL -> WebSocket.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.ai_predictor import ai_predictor_service
from app.services.feature_assembler import FeatureAssembler
from app.database.repositories import RiskPredictionRepository
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


class PredictionService:
    """Orchestrates AI feature assembly, inference, database persistence, and WebSocket broadcasting."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db
        self.ai_service = ai_predictor_service
        self.assembler = FeatureAssembler(db=db)

    @property
    def is_loaded(self) -> bool:
        return self.ai_service.is_loaded

    def predict(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Direct call to AI predictor."""
        return self.ai_service.predict(record)

    async def execute_prediction(
        self,
        req: PredictionRequest,
        db: Session,
        telemetry: Optional[Dict[str, Any]] = None
    ) -> PredictionResponse:
        """
        Execute prediction pipeline:
        1. Feature Assembly & Data Freshness Check
        2. Run AI Predictor (LandslidePredictor)
        3. Save RiskPrediction in MySQL
        4. Broadcast WebSocket risk update (with optional telemetry)
        """
        loc_dict = req.location.model_dump()
        rainfall_dict = req.rainfall.model_dump() if req.rainfall else None
        soil_dict = req.soil.model_dump() if req.soil else None
        terrain_dict = req.terrain.model_dump() if req.terrain else None

        # 1. Assemble feature record
        raw_record, data_status, missing = self.assembler.assemble_record(
            location=loc_dict,
            rainfall=rainfall_dict,
            soil=soil_dict,
            terrain=terrain_dict,
            timestamp=req.timestamp
        )

        if data_status == "INSUFFICIENT_DATA":
            raise ValueError(f"Insufficient feature data for prediction: {missing}")

        # 2. Run AI inference
        ai_res = self.ai_service.predict(raw_record)

        now_dt = datetime.now(timezone.utc)
        lat = req.location.latitude
        lon = req.location.longitude

        # 3. Save to database
        risk_repo = RiskPredictionRepository(db)
        pred_record = risk_repo.create({
            "latitude": lat,
            "longitude": lon,
            "risk_probability": ai_res["landslide_probability"],
            "risk_score": ai_res["risk_score"],
            "risk_level": ai_res["risk_level"],
            "data_status": data_status,
            "model_version": ai_res["model_version"],
            "prediction_timestamp": now_dt
        })

        resp = PredictionResponse(
            prediction_id=pred_record.id,
            latitude=lat,
            longitude=lon,
            landslide_probability=ai_res["landslide_probability"],
            risk_score=ai_res["risk_score"],
            risk_level=ai_res["risk_level"],
            data_status=data_status,
            model_version=ai_res["model_version"],
            timestamp=now_dt.isoformat()
        )

        # 4. Broadcast live risk update to all active WebSocket clients (Phase 12 & 13)
        if manager.client_count > 0:
            msg_data = resp.model_dump()
            if telemetry:
                msg_data["telemetry"] = telemetry

            ws_message = {
                "type": "risk_update",
                "data": msg_data
            }
            await manager.broadcast(ws_message)
            logger.info(f"Broadcasted live risk update (status: {data_status}) to {manager.client_count} WebSocket clients.")

        return resp



def get_prediction_service() -> PredictionService:
    return PredictionService()
