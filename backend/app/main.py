"""
Main FastAPI Application Entry Point for SATHI Landslide Early-Warning Backend.
Configures lifespan, CORS, database initialization, AI model preloading,
background risk monitoring worker, REST API routers, and WebSockets.
"""

import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import setup_logging
from app.database.connection import init_db, get_db

from app.services.ai_predictor import ai_predictor_service, get_ai_predictor, AIPredictionService
from app.workers.risk_monitor import risk_monitor_worker
from app.websocket.manager import manager

# Route Imports
from app.api.v1.endpoints import predictions, sensors, weather, reports, volunteers, risk, zones, model, inventory, dashboard, disaster
from app.websocket import routes as ws_routes

setup_logging()
logger = logging.getLogger("backend_main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Lifespan Context Manager."""
    logger.info("Initializing SATHI Backend Services...")

    # 1. Initialize DB tables if SQLite fallback
    init_db()

    # 2. Preload AI Model once
    ai_predictor_service.load_model()

    # 3. Start Background Risk Monitoring Worker
    risk_monitor_worker.start()

    logger.info("SATHI Backend initialized successfully!")
    yield

    # Shutdown
    await risk_monitor_worker.stop()
    logger.info("SATHI Backend shutdown complete.")




app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SATHI Landslide Early-Warning Backend API & AI Engine",
    version=settings.MODEL_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_cors_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mounting REST Routers
app.include_router(predictions.router, prefix=f"{settings.API_V1_STR}/predictions", tags=["Predictions"])
app.include_router(sensors.router, prefix=f"{settings.API_V1_STR}/sensors", tags=["Sensors"])
app.include_router(weather.router, prefix=f"{settings.API_V1_STR}/weather", tags=["Weather"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])
app.include_router(volunteers.router, prefix=f"{settings.API_V1_STR}/volunteers", tags=["Volunteers"])
app.include_router(risk.router, prefix=f"{settings.API_V1_STR}/risk", tags=["Risk"])
app.include_router(zones.router, prefix=f"{settings.API_V1_STR}", tags=["Zones"])
app.include_router(model.router, prefix=f"{settings.API_V1_STR}/model", tags=["Model"])
app.include_router(inventory.router, prefix=f"{settings.API_V1_STR}", tags=["Inventory"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(disaster.router, prefix=f"{settings.API_V1_STR}/disaster", tags=["Disaster ML"])

# Mount Native WebSocket Router
app.include_router(ws_routes.router, tags=["WebSockets"])


# Root Aliases for Frontend Compatibility
@app.get("/dashboard/overview", tags=["Dashboard Alias"])
def get_dashboard_overview_root_alias(db: Session = Depends(get_db)):
    return dashboard.get_dashboard_overview(db=db)

@app.get("/zones", tags=["Zones Alias"])
def get_zones_root_alias():
    return zones.get_risk_zones(ai_service=ai_predictor_service)

@app.get("/inventory/landslides", tags=["Inventory Alias"])
def get_inventory_landslides_root_alias(state: str = None, limit: int = 200, offset: int = 0):
    return inventory.get_landslide_inventory(state=state, limit=limit, offset=offset)

@app.get("/inventory/stats", tags=["Inventory Alias"])
def get_inventory_stats_root_alias():
    return inventory.get_inventory_stats()

@app.post("/reports", tags=["Reports Alias"])
@app.post("/api/reports", tags=["Reports Alias"])
def create_report_root_alias(report: reports.CitizenReportCreate, db: Session = Depends(get_db)):
    return reports.submit_citizen_report(report=report, db=db)

@app.get("/reports", tags=["Reports Alias"])
@app.get("/api/reports", tags=["Reports Alias"])
def get_reports_root_alias(limit: int = 100, db: Session = Depends(get_db)):
    return reports.get_citizen_reports(limit=limit, db=db)

@app.put("/reports/{report_id}/verify", tags=["Reports Alias"])
@app.put("/api/reports/{report_id}/verify", tags=["Reports Alias"])
def verify_report_root_alias(report_id: int, payload: reports.CitizenReportVerify, db: Session = Depends(get_db)):
    return reports.verify_citizen_report(report_id=report_id, payload=payload, db=db)

@app.post("/volunteers", tags=["Volunteers Alias"])
@app.post("/api/volunteers", tags=["Volunteers Alias"])
def create_volunteer_root_alias(payload: volunteers.VolunteerOfferCreate, db: Session = Depends(get_db)):
    return volunteers.submit_volunteer_offer(payload=payload, db=db)

@app.get("/volunteers", tags=["Volunteers Alias"])
@app.get("/api/volunteers", tags=["Volunteers Alias"])
def get_volunteers_root_alias(limit: int = 100, db: Session = Depends(get_db)):
    return volunteers.get_volunteer_offers(limit=limit, db=db)

@app.put("/volunteers/{offer_id}/status", tags=["Volunteers Alias"])
@app.put("/api/volunteers/{offer_id}/status", tags=["Volunteers Alias"])
def update_volunteer_status_alias(offer_id: int, payload: volunteers.VolunteerOfferUpdateStatus, db: Session = Depends(get_db)):
    return volunteers.update_volunteer_status(offer_id=offer_id, payload=payload, db=db)


@app.get("/model/status", tags=["Model Alias"])
@app.get("/api/model/status", tags=["Model Alias"])
def get_model_status_root_alias(ai_service: AIPredictionService = Depends(get_ai_predictor)):
    return model.get_model_status(ai_service=ai_service)


@app.get("/health", tags=["Health"])
def health_check():
    """Health & Readiness Status Endpoint."""
    model_status = "loaded" if ai_predictor_service.is_loaded else "unavailable"
    version = ai_predictor_service.predictor.model_version if ai_predictor_service.is_loaded and ai_predictor_service.predictor else "unknown"

    return {
        "status": "ok",
        "database": "connected",
        "model": {
            "loaded": ai_predictor_service.is_loaded,
            "version": version
        },
        "websocket_clients": manager.client_count,
        "risk_monitor": {
            "running": risk_monitor_worker._running,
            "interval_seconds": settings.RISK_UPDATE_INTERVAL_SECONDS
        }
    }
