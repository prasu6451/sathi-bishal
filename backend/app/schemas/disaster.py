"""
Pydantic Data Validation Schemas for Multi-Hazard Flood Disaster Management API.
Supports all 7 modules: Flood Severity, Rescue Priority, Resource Allocation,
Area Clustering, SOS NLP Classification, Damage Assessment, and Safe Route Planning.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# 1. Flood Severity
class FloodSeverityRequest(BaseModel):
    rainfall_24h_mm: float = Field(..., ge=0.0, description="24-hour antecedent rainfall in mm")
    rainfall_7d_mm: float = Field(default=0.0, ge=0.0, description="7-day cumulative rainfall in mm")
    soil_moisture: float = Field(default=0.45, ge=0.0, le=1.0, description="Volumetric soil moisture (0 to 1)")
    elevation_m: float = Field(default=100.0, description="Terrain elevation in meters")
    slope_deg: float = Field(default=5.0, description="Terrain slope in degrees")
    river_distance_m: float = Field(default=500.0, description="Distance to closest river/waterway in meters")


class FloodSeverityResponse(BaseModel):
    severity_index: float
    severity_level: str
    estimated_water_depth_m: float
    color_code: str
    evacuation_recommended: bool
    metrics: Dict[str, Any]


# 2. Rescue Priority
class RescuePriorityRequest(BaseModel):
    area_name: str = Field(..., description="Name of affected district or community")
    population_density_sqkm: float = Field(..., ge=1.0, description="Estimated population density per sq km")
    sos_count: int = Field(..., ge=0, description="Number of active emergency SOS alerts")
    vulnerability_index: float = Field(default=0.5, ge=0.0, le=1.0, description="Proportion of elderly/children/sick (0 to 1)")
    flood_depth_m: float = Field(default=1.0, ge=0.0, description="Current or predicted flood water depth in meters")
    road_accessibility_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Accessible road network percentage")


class RescuePriorityResponse(BaseModel):
    area_name: str
    urgency_score: float
    priority_tier: str
    recommended_action: str
    badge_color: str
    critical_factors: Dict[str, Any]


# 3. Resource Allocation
class ResourceAllocationRequest(BaseModel):
    affected_population: int = Field(..., ge=1, description="Total affected population count")
    severity_index: float = Field(..., ge=0.0, le=1.0, description="Disaster severity index (0 to 1)")
    duration_days: int = Field(default=3, ge=1, le=30, description="Relief operation duration window in days")
    medical_incident_count: int = Field(default=0, ge=0, description="Reported medical emergency incidents")


class ResourceAllocationResponse(BaseModel):
    affected_population: int
    duration_days: int
    allocations: Dict[str, Any]
    logistical_summary: str


# 4. Area Clustering
class LocationImpactItem(BaseModel):
    id: Optional[str] = None
    name: str
    latitude: float
    longitude: float
    severity_index: float = Field(..., ge=0.0, le=1.0)
    sos_count: int = Field(default=0, ge=0)


class AreaClusteringRequest(BaseModel):
    locations: List[LocationImpactItem]
    clusters: int = Field(default=3, ge=1, le=10)


class AreaClusteringResponse(BaseModel):
    total_locations: int
    cluster_count: int
    clustered_locations: List[Dict[str, Any]]


# 5. SOS NLP Classification
class SOSClassificationRequest(BaseModel):
    message: str = Field(..., min_length=2, description="Citizen emergency text message or SOS report")


class SOSClassificationResponse(BaseModel):
    category: str
    category_display: str
    urgency: str
    confidence: float
    is_critical: bool
    extracted_keywords: List[str]
    probabilities: Dict[str, float]


# 6. Damage Assessment
class DamageAssessmentRequest(BaseModel):
    structure_type: str = Field(default="BUILDING", description="BUILDING, ROAD, BRIDGE, or POWER_GRID")
    flood_depth_m: float = Field(..., ge=0.0, description="Flood water depth against structure")
    water_flow_velocity_mps: float = Field(default=1.5, ge=0.0, description="Water velocity in m/s")
    structure_age_years: int = Field(default=15, ge=0, description="Age of structure in years")
    construction_material: str = Field(default="CONCRETE", description="MUD_BRICK, TIMBER, MASONRY, CONCRETE, or STEEL")


class DamageAssessmentResponse(BaseModel):
    structure_type: str
    damage_index: float
    damage_percentage: float
    functional_status: str
    safety_assessment: str
    color_badge: str
    reconstruction_cost_index: float


# 7. Safe Route
class CoordinatePoint(BaseModel):
    latitude: float
    longitude: float


class HazardZoneInput(BaseModel):
    latitude: float
    longitude: float
    severity: float = Field(default=0.8, ge=0.0, le=1.0)
    hazard_type: str = Field(default="FLOOD", description="FLOOD or LANDSLIDE")


class SafeRouteRequest(BaseModel):
    origin: CoordinatePoint
    destination: CoordinatePoint
    hazard_zones: Optional[List[HazardZoneInput]] = None


class SafeRouteResponse(BaseModel):
    origin: Dict[str, float]
    destination: Dict[str, float]
    direct_distance_km: float
    safe_distance_km: float
    estimated_travel_time_mins: int
    safety_score_pct: float
    hazard_zones_avoided: int
    safe_route_waypoints: List[List[float]]
    direct_hazard_waypoints: List[List[float]]
    navigation_instruction: str


# 8. Unified Pipeline
class UnifiedDisasterReportRequest(BaseModel):
    area_name: str
    latitude: float
    longitude: float
    rainfall_24h_mm: float
    rainfall_7d_mm: float = 0.0
    soil_moisture: float = 0.5
    elevation_m: float = 120.0
    slope_deg: float = 4.0
    population: int = 1500
    sos_messages: Optional[List[str]] = None


class UnifiedDisasterReportResponse(BaseModel):
    area_name: str
    latitude: float
    longitude: float
    flood_severity: FloodSeverityResponse
    rescue_priority: RescuePriorityResponse
    resource_allocation: ResourceAllocationResponse
    sos_analysis: List[SOSClassificationResponse]
    damage_overview: DamageAssessmentResponse
    executive_summary: str
