"""Report Service layer for Citizen Reports."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.repositories import CitizenReportRepository


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CitizenReportRepository(db)

    def submit_report(self, data: Dict[str, Any]):
        return self.repo.create_report(
            lat=data["latitude"],
            lon=data["longitude"],
            severity=data.get("severity", 1),
            description=data.get("description", ""),
            image_url=data.get("image_url")
        )
