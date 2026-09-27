"""Risk Service layer for Risk History & Map Data."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.repositories import RiskPredictionRepository


class RiskService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RiskPredictionRepository(db)

    def get_latest_map(self):
        return self.repo.get_latest_predictions_all_locations()

    def get_history(self, limit: int = 100):
        return self.repo.get_history(limit=limit)
