"""
API v1 Master Router aggregating endpoint sub-modules.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, predict, reports, zones

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(predict.router, tags=["Landslide Prediction & Risk Monitoring"])
api_router.include_router(reports.router, tags=["Citizen Reports"])
api_router.include_router(zones.router, tags=["Risk Zones"])
