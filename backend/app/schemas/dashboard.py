"""
Pydantic V2 Schemas for Operational Dashboard Endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class StatCardItem(BaseModel):
    label: str
    value: str
    delta: str
    tone: str


class ZoneSummaryItem(BaseModel):
    district: str
    flood: int
    landslide: int
    status: str


class AlertItem(BaseModel):
    type: str
    title: str
    time: str
    severity: str
    description: str


class TrendDataItem(BaseModel):
    label: str
    value: int


class DashboardOverviewResponse(BaseModel):
    stat_cards: List[StatCardItem]
    zone_summary: List[ZoneSummaryItem]
    alerts: List[AlertItem]
    trend_data: List[TrendDataItem]
    recommendations: List[str]


class AlertCreate(BaseModel):
    type: str = Field(..., description="Alert type (Flood, Landslide, Rainfall)")
    title: str = Field(..., description="Alert title")
    severity: str = Field(..., description="Severity level (Low, Moderate, High, Critical)")
    description: str = Field(..., description="Detailed description")
    time_ago: Optional[str] = Field(default="Just now")

