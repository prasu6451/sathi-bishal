"""
Citizen Reports REST Endpoints matching Section 5 & 18 of Master Prompt.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.report import CitizenReportCreate, CitizenReportResponse
from app.services.report_service import ReportService

router = APIRouter()


@router.post("", response_model=CitizenReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(payload: CitizenReportCreate, db: Session = Depends(get_db)) -> CitizenReportResponse:
    """File a citizen landslide observation report."""
    service = ReportService(db)
    return service.create_report(payload.model_dump())


@router.get("", response_model=List[CitizenReportResponse])
def get_reports(limit: int = 50, db: Session = Depends(get_db)) -> List[CitizenReportResponse]:
    """Retrieve citizen landslide observation reports."""
    service = ReportService(db)
    return service.get_reports(limit=limit)


@router.get("/{report_id}", response_model=CitizenReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)) -> CitizenReportResponse:
    """Get report details by report_id."""
    service = ReportService(db)
    report = service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report '{report_id}' not found")
    return report
