"""
Disaster ML Service for FastAPI Backend.
Integrates all 7 Flood Disaster Management ML models into production API execution.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("disaster_ml_service")

# Ensure project root in sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ai.models.flood_disaster_models import (
    flood_severity_model,
    rescue_priority_model,
    resource_allocation_model,
    area_clustering_model,
    sos_nlp_classifier,
    damage_assessment_model,
    safe_route_engine
)


class DisasterMLService:
    """Singleton service providing multi-hazard flood disaster ML inference."""

    def __init__(self) -> None:
        self.is_loaded = True
        logger.info("DisasterMLService initialized with all 7 ML disaster modules.")

    def assess_flood_severity(
        self,
        rainfall_24h_mm: float,
        rainfall_7d_mm: float,
        soil_moisture: float,
        elevation_m: float,
        slope_deg: float,
        river_distance_m: float = 500.0
    ) -> Dict[str, Any]:
        return flood_severity_model.assess(
            rainfall_24h_mm=rainfall_24h_mm,
            rainfall_7d_mm=rainfall_7d_mm,
            soil_moisture=soil_moisture,
            elevation_m=elevation_m,
            slope_deg=slope_deg,
            river_distance_m=river_distance_m
        )

    def calculate_rescue_priority(
        self,
        area_name: str,
        population_density_sqkm: float,
        sos_count: int,
        vulnerability_index: float,
        flood_depth_m: float,
        road_accessibility_pct: float
    ) -> Dict[str, Any]:
        res = rescue_priority_model.calculate_priority_score(
            population_density_sqkm=population_density_sqkm,
            sos_count=sos_count,
            vulnerability_index=vulnerability_index,
            flood_depth_m=flood_depth_m,
            road_accessibility_pct=road_accessibility_pct
        )
        return {"area_name": area_name, **res}

    def allocate_resources(
        self,
        affected_population: int,
        severity_index: float,
        duration_days: int = 3,
        medical_incident_count: int = 0
    ) -> Dict[str, Any]:
        return resource_allocation_model.allocate(
            affected_population=affected_population,
            severity_index=severity_index,
            duration_days=duration_days,
            medical_incident_count=medical_incident_count
        )

    def cluster_areas(self, locations: List[Dict[str, Any]], k: int = 3) -> Dict[str, Any]:
        clustered = area_clustering_model.cluster_locations(locations, k=k)
        return {
            "total_locations": len(locations),
            "cluster_count": k,
            "clustered_locations": clustered
        }

    def classify_sos_message(self, message: str) -> Dict[str, Any]:
        return sos_nlp_classifier.classify(message)

    def assess_damage(
        self,
        structure_type: str,
        flood_depth_m: float,
        water_flow_velocity_mps: float,
        structure_age_years: int = 15,
        construction_material: str = "CONCRETE"
    ) -> Dict[str, Any]:
        return damage_assessment_model.assess_damage(
            structure_type=structure_type,
            flood_depth_m=flood_depth_m,
            water_flow_velocity_mps=water_flow_velocity_mps,
            structure_age_years=structure_age_years,
            construction_material=construction_material
        )

    def compute_safe_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        hazard_zones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return safe_route_engine.compute_safe_route(
            origin=origin,
            destination=destination,
            hazard_zones=hazard_zones
        )

    def generate_unified_report(
        self,
        area_name: str,
        latitude: float,
        longitude: float,
        rainfall_24h_mm: float,
        rainfall_7d_mm: float,
        soil_moisture: float,
        elevation_m: float,
        slope_deg: float,
        population: int,
        sos_messages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        # 1. Flood severity
        f_sev = self.assess_flood_severity(
            rainfall_24h_mm=rainfall_24h_mm,
            rainfall_7d_mm=rainfall_7d_mm,
            soil_moisture=soil_moisture,
            elevation_m=elevation_m,
            slope_deg=slope_deg
        )

        # 2. SOS messages analysis
        sos_msgs = sos_messages or [f"Immediate help needed in {area_name}, flood waters rising past ground floor!"]
        sos_results = [self.classify_sos_message(msg) for msg in sos_msgs]
        critical_count = sum(1 for s in sos_results if s["is_critical"])

        # 3. Rescue priority
        rescue_res = self.calculate_rescue_priority(
            area_name=area_name,
            population_density_sqkm=population / 2.0,
            sos_count=len(sos_msgs) * 3,
            vulnerability_index=0.60,
            flood_depth_m=f_sev["estimated_water_depth_m"],
            road_accessibility_pct=max(10.0, 100.0 - f_sev["severity_index"] * 100.0)
        )

        # 4. Resource allocation
        alloc_res = self.allocate_resources(
            affected_population=population,
            severity_index=f_sev["severity_index"],
            duration_days=3,
            medical_incident_count=critical_count
        )

        # 5. Damage assessment
        damage_res = self.assess_damage(
            structure_type="BUILDING",
            flood_depth_m=f_sev["estimated_water_depth_m"],
            water_flow_velocity_mps=1.8,
            structure_age_years=20,
            construction_material="MASONRY"
        )

        summary = (
            f"DISASTER SITUATION REPORT FOR {area_name.upper()}: "
            f"Flood severity is {f_sev['severity_level']} (est. depth {f_sev['estimated_water_depth_m']}m). "
            f"Assigned rescue ranking is {rescue_res['priority_tier']} with recommended action: '{rescue_res['recommended_action']}'. "
            f"Recommended dispatch includes {alloc_res['allocations']['clean_water_litres']:,}L potable water and "
            f"{alloc_res['allocations']['medical_trauma_kits']} medical trauma kits."
        )

        return {
            "area_name": area_name,
            "latitude": latitude,
            "longitude": longitude,
            "flood_severity": f_sev,
            "rescue_priority": rescue_res,
            "resource_allocation": alloc_res,
            "sos_analysis": sos_results,
            "damage_overview": damage_res,
            "executive_summary": summary
        }


# Singleton service
disaster_ml_service = DisasterMLService()


def get_disaster_ml_service() -> DisasterMLService:
    return disaster_ml_service
