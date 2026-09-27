"""
REST API Endpoints for Multi-Hazard Disaster Management ML Suite.
Mounts under /api/v1/disaster.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException

from app.schemas.disaster import (
    FloodSeverityRequest, FloodSeverityResponse,
    RescuePriorityRequest, RescuePriorityResponse,
    ResourceAllocationRequest, ResourceAllocationResponse,
    AreaClusteringRequest, AreaClusteringResponse,
    SOSClassificationRequest, SOSClassificationResponse,
    DamageAssessmentRequest, DamageAssessmentResponse,
    SafeRouteRequest, SafeRouteResponse,
    UnifiedDisasterReportRequest, UnifiedDisasterReportResponse
)
from app.services.disaster_ml_service import get_disaster_ml_service, DisasterMLService

router = APIRouter()


@router.post("/flood-severity", response_model=FloodSeverityResponse, tags=["Disaster ML"])
def assess_flood_severity(
    payload: FloodSeverityRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 1: Flood Severity Assessment & Water Depth Estimation."""
    return service.assess_flood_severity(
        rainfall_24h_mm=payload.rainfall_24h_mm,
        rainfall_7d_mm=payload.rainfall_7d_mm,
        soil_moisture=payload.soil_moisture,
        elevation_m=payload.elevation_m,
        slope_deg=payload.slope_deg,
        river_distance_m=payload.river_distance_m
    )


@router.post("/rescue-priority", response_model=RescuePriorityResponse, tags=["Disaster ML"])
def calculate_rescue_priority(
    payload: RescuePriorityRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 2: Rescue Priority Identification (Random Forest Ranking)."""
    return service.calculate_rescue_priority(
        area_name=payload.area_name,
        population_density_sqkm=payload.population_density_sqkm,
        sos_count=payload.sos_count,
        vulnerability_index=payload.vulnerability_index,
        flood_depth_m=payload.flood_depth_m,
        road_accessibility_pct=payload.road_accessibility_pct
    )


@router.post("/resource-allocation", response_model=ResourceAllocationResponse, tags=["Disaster ML"])
def allocate_resources(
    payload: ResourceAllocationRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 3: Resource Allocation Optimization (XGBoost)."""
    return service.allocate_resources(
        affected_population=payload.affected_population,
        severity_index=payload.severity_index,
        duration_days=payload.duration_days,
        medical_incident_count=payload.medical_incident_count
    )


@router.post("/cluster-areas", response_model=AreaClusteringResponse, tags=["Disaster ML"])
def cluster_areas(
    payload: AreaClusteringRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 4: Area Severity Clustering (K-Means)."""
    locs_data = [loc.model_dump() for loc in payload.locations]
    return service.cluster_areas(locs_data, k=payload.clusters)


@router.post("/classify-sos", response_model=SOSClassificationResponse, tags=["Disaster ML"])
def classify_sos_message(
    payload: SOSClassificationRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 5: SOS Request NLP Classifier (Transformer / Multi-Class NLP)."""
    return service.classify_sos_message(payload.message)


@router.post("/damage-assessment", response_model=DamageAssessmentResponse, tags=["Disaster ML"])
def assess_damage(
    payload: DamageAssessmentRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 6: Infrastructure Damage Assessment."""
    return service.assess_damage(
        structure_type=payload.structure_type,
        flood_depth_m=payload.flood_depth_m,
        water_flow_velocity_mps=payload.water_flow_velocity_mps,
        structure_age_years=payload.structure_age_years,
        construction_material=payload.construction_material
    )


@router.post("/safe-route", response_model=SafeRouteResponse, tags=["Disaster ML"])
def compute_safe_route(
    payload: SafeRouteRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Module 7: Safe Evacuation Route Recommendation Engine."""
    hz_list = [h.model_dump() for h in payload.hazard_zones] if payload.hazard_zones else []
    return service.compute_safe_route(
        origin=(payload.origin.latitude, payload.origin.longitude),
        destination=(payload.destination.latitude, payload.destination.longitude),
        hazard_zones=hz_list
    )


@router.post("/unified-pipeline", response_model=UnifiedDisasterReportResponse, tags=["Disaster ML"])
def generate_unified_report(
    payload: UnifiedDisasterReportRequest,
    service: DisasterMLService = Depends(get_disaster_ml_service)
):
    """Unified Orchestration Pipeline: Combines all models into one Situation Report."""
    return service.generate_unified_report(
        area_name=payload.area_name,
        latitude=payload.latitude,
        longitude=payload.longitude,
        rainfall_24h_mm=payload.rainfall_24h_mm,
        rainfall_7d_mm=payload.rainfall_7d_mm,
        soil_moisture=payload.soil_moisture,
        elevation_m=payload.elevation_m,
        slope_deg=payload.slope_deg,
        population=payload.population,
        sos_messages=payload.sos_messages
    )
