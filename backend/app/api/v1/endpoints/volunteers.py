"""Volunteer Offers & Help Applications REST API Endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.repositories import VolunteerOfferRepository
from app.schemas.volunteer import VolunteerOfferCreate, VolunteerOfferResponse, VolunteerOfferUpdateStatus

router = APIRouter()


def _format_offer_response(off) -> VolunteerOfferResponse:
    return VolunteerOfferResponse(
        id=off.id,
        volunteer_name=off.volunteer_name,
        volunteer_phone=off.volunteer_phone,
        volunteer_email=off.volunteer_email,
        help_type=off.help_type or "General Relief",
        location_name=off.location_name,
        latitude=off.latitude,
        longitude=off.longitude,
        target_report_id=off.target_report_id,
        message=off.message,
        status=off.status or "OFFERED",
        created_at=off.created_at.isoformat() if hasattr(off.created_at, 'isoformat') else str(off.created_at)
    )


@router.post("", response_model=VolunteerOfferResponse, status_code=status.HTTP_201_CREATED)
def submit_volunteer_offer(payload: VolunteerOfferCreate, db: Session = Depends(get_db)):
    """Submit a volunteer offer/application to assist affected citizens."""
    repo = VolunteerOfferRepository(db)
    offer = repo.create_offer(
        volunteer_name=payload.volunteer_name,
        volunteer_phone=payload.volunteer_phone,
        volunteer_email=payload.volunteer_email,
        help_type=payload.help_type,
        location_name=payload.location_name,
        lat=payload.latitude,
        lon=payload.longitude,
        target_report_id=payload.target_report_id,
        message=payload.message
    )
    return _format_offer_response(offer)


@router.get("", response_model=List[VolunteerOfferResponse])
def get_volunteer_offers(limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve list of all volunteer help offers."""
    repo = VolunteerOfferRepository(db)
    offers = repo.get_all(limit=limit)
    return [_format_offer_response(o) for o in offers]


@router.put("/{offer_id}/status", response_model=VolunteerOfferResponse)
@router.patch("/{offer_id}/status", response_model=VolunteerOfferResponse)
def update_volunteer_status(offer_id: int, payload: VolunteerOfferUpdateStatus, db: Session = Depends(get_db)):
    """Update status of a volunteer offer (e.g. OFFERED, ASSIGNED, COMPLETED, REJECTED)."""
    repo = VolunteerOfferRepository(db)
    updated = repo.update_status(offer_id=offer_id, status=payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Volunteer offer #{offer_id} not found")
    return _format_offer_response(updated)
