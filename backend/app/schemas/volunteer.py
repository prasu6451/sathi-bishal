"""Pydantic schemas for Volunteer Offers / Applications."""
from pydantic import BaseModel
from typing import Optional


class VolunteerOfferCreate(BaseModel):
    volunteer_name: str
    volunteer_phone: str
    volunteer_email: Optional[str] = None
    help_type: str = "General Relief"
    location_name: str
    latitude: float
    longitude: float
    target_report_id: Optional[int] = None
    message: Optional[str] = None


class VolunteerOfferUpdateStatus(BaseModel):
    status: str
    admin_notes: Optional[str] = None


class VolunteerOfferResponse(BaseModel):
    id: int
    volunteer_name: str
    volunteer_phone: str
    volunteer_email: Optional[str] = None
    help_type: str
    location_name: str
    latitude: float
    longitude: float
    target_report_id: Optional[int] = None
    message: Optional[str] = None
    status: str
    created_at: str

    class Config:
        from_attributes = True
