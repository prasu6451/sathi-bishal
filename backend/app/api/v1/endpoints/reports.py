"""Citizen Reports API Endpoint."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repositories import CitizenReportRepository
from app.schemas.report import CitizenReportCreate, CitizenReportResponse, CitizenReportVerify

router = APIRouter()


def _format_report_response(rep) -> CitizenReportResponse:
    v_at = getattr(rep, 'verified_at', None)
    return CitizenReportResponse(
        id=rep.id,
        latitude=rep.latitude,
        longitude=rep.longitude,
        severity=rep.severity,
        disaster_type=getattr(rep, 'disaster_type', 'landslide'),
        risk_level=getattr(rep, 'risk_level', 'moderate'),
        location_name=getattr(rep, 'location_name', None),
        reporter_name=getattr(rep, 'reporter_name', None),
        reporter_phone=getattr(rep, 'reporter_phone', None),
        description=rep.description,
        image_url=rep.image_url,
        verification_status=getattr(rep, 'verification_status', 'PENDING') or 'PENDING',
        authority_notes=getattr(rep, 'authority_notes', None),
        verified_by=getattr(rep, 'verified_by', None),
        verified_at=v_at.isoformat() if v_at else None,
        created_at=rep.created_at.isoformat() if hasattr(rep.created_at, 'isoformat') else str(rep.created_at)
    )


@router.post("", response_model=CitizenReportResponse, status_code=status.HTTP_201_CREATED)
def submit_citizen_report(report: CitizenReportCreate, db: Session = Depends(get_db)):
    """
    Submit citizen report.
    Stored for monitoring & dashboard display, but strictly EXCLUDED from predictive AI model input.
    """
    repo = CitizenReportRepository(db)

    sev_map = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
    severity_val = report.severity or sev_map.get((report.risk_level or "").lower(), 2)
    lat_val = report.latitude if report.latitude is not None else 26.1445
    lon_val = report.longitude if report.longitude is not None else 91.7362

    rep = repo.create_report(
        lat=lat_val,
        lon=lon_val,
        severity=severity_val,
        disaster_type=report.disaster_type or "landslide",
        risk_level=report.risk_level or "moderate",
        location_name=report.location_name,
        reporter_name=report.reporter_name,
        reporter_phone=report.reporter_phone,
        description=report.description or "",
        image_url=report.image_url
    )

    return _format_report_response(rep)


@router.get("", response_model=List[CitizenReportResponse])
def get_citizen_reports(limit: int = 100, db: Session = Depends(get_db)):
    """Fetch citizen reports."""
    repo = CitizenReportRepository(db)
    reports = repo.get_all(limit=limit)
    return [_format_report_response(r) for r in reports]


@router.put("/{report_id}/verify", response_model=CitizenReportResponse)
@router.patch("/{report_id}/verify", response_model=CitizenReportResponse)
def verify_citizen_report(report_id: int, payload: CitizenReportVerify, db: Session = Depends(get_db)):
    """Authority verification & marking endpoint for citizen reports."""
    repo = CitizenReportRepository(db)
    updated = repo.verify_report(
        report_id=report_id,
        verification_status=payload.verification_status,
        authority_notes=payload.authority_notes,
        verified_by=payload.verified_by or "Admin Authority"
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"Report #{report_id} not found")
    return _format_report_response(updated)

