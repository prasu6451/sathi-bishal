"""
Initial Data Seeder for SATHI Landslide & Flood Monitoring Operations.
Populates authoritative records derived from the 11,026 SIH26001 Geological Dataset.
"""

import logging
from sqlalchemy.orm import Session
from app.database.models import (
    MonitoredLocation, Sensor, DashboardStat, DistrictRiskSummary,
    SystemAlert, RiskTrend, ActionRecommendation, VolunteerOffer
)

logger = logging.getLogger(__name__)


def seed_initial_data(db: Session) -> None:
    """Populate default operational dashboard data and monitored locations derived from 11,026 SIH26001 dataset."""
    try:
        # 1. Monitored Locations
        if db.query(MonitoredLocation).count() == 0:
            locations = [
                MonitoredLocation(name="Aizawl Ridge & Slopes (Mizoram - 1,317 Dataset Incidents)", latitude=23.73, longitude=92.72),
                MonitoredLocation(name="Lunglei Hill Corridor (Mizoram - 669 Dataset Incidents)", latitude=22.88, longitude=92.73),
                MonitoredLocation(name="Kohima Town Slopes (Nagaland - 487 Dataset Incidents)", latitude=25.65, longitude=94.10),
                MonitoredLocation(name="East Khasi Hills / Shillong (Meghalaya - 405 Dataset Incidents)", latitude=25.55, longitude=91.90),
                MonitoredLocation(name="Dima Hasao Foothills (Assam - 387 Dataset Incidents)", latitude=25.18, longitude=93.02),
                MonitoredLocation(name="Ukhrul Border Slopes (Manipur - 315 Dataset Incidents)", latitude=24.82, longitude=93.95),
                MonitoredLocation(name="Guwahati Ridge & South Slope (Assam)", latitude=26.15, longitude=91.75),
                MonitoredLocation(name="Gangtok Ridge & Teesta Gorge (Sikkim)", latitude=27.33, longitude=88.62)
            ]
            db.add_all(locations)
            db.commit()
            logger.info(f"Seeded {len(locations)} MonitoredLocations.")

        # 2. IoT Sensors
        if db.query(Sensor).count() == 0:
            sensors = [
                Sensor(sensor_id="SENSOR_AIZAWL", name="Aizawl Ridge Station (Mizoram)", latitude=23.73, longitude=92.72, sensor_type="inclinometer"),
                Sensor(sensor_id="SENSOR_LUNGLEI", name="Lunglei Hill Station (Mizoram)", latitude=22.88, longitude=92.73, sensor_type="inclinometer"),
                Sensor(sensor_id="SENSOR_KOHIMA", name="Kohima Town Station (Nagaland)", latitude=25.65, longitude=94.10, sensor_type="rain_gauge"),
                Sensor(sensor_id="SENSOR_SHILLONG", name="Shillong Station (Meghalaya)", latitude=25.55, longitude=91.90, sensor_type="rain_gauge"),
                Sensor(sensor_id="SENSOR_DIMA_HASAO", name="Dima Hasao Station (Assam)", latitude=25.18, longitude=93.02, sensor_type="piezometer"),
                Sensor(sensor_id="SENSOR_UKHRUL", name="Ukhrul Station (Manipur)", latitude=24.82, longitude=93.95, sensor_type="rain_gauge"),
                Sensor(sensor_id="SENSOR_GUWAHATI", name="Guwahati Station (Assam)", latitude=26.15, longitude=91.75, sensor_type="rain_gauge"),
                Sensor(sensor_id="SENSOR_GANGTOK", name="Gangtok Station (Sikkim)", latitude=27.33, longitude=88.62, sensor_type="inclinometer")
            ]
            db.add_all(sensors)
            db.commit()
            logger.info(f"Seeded {len(sensors)} Sensors.")

        # 3. Dashboard Stats
        if db.query(DashboardStat).count() == 0:
            stats = [
                DashboardStat(stat_key="flood_alerts", label="Flood alerts", value="14", delta="+4 since yesterday", tone="flood"),
                DashboardStat(stat_key="landslide_watch", label="Landslide watch", value="11,026", delta="SIH26001 dataset incidents", tone="landslide"),
                DashboardStat(stat_key="people_at_risk", label="People at risk", value="5.8K", delta="Across 8 NE districts", tone="risk"),
                DashboardStat(stat_key="rainfall_forecast", label="Rainfall forecast", value="84 mm", delta="24h cumulative forecast", tone="rain")
            ]
            db.add_all(stats)
            db.commit()
            logger.info("Seeded DashboardStats.")

        # 4. District Risk Summaries (Mapped from 11,026 SIH26001 Dataset Counts)
        # Clear out existing if table was populated with initial mock data
        db.query(DistrictRiskSummary).delete()
        db.commit()

        summaries = [
            DistrictRiskSummary(district="Aizawl (1,317 Dataset Incidents)", state="Mizoram", flood_risk_pct=35.0, landslide_risk_pct=94.0, status="Critical", people_at_risk=1320),
            DistrictRiskSummary(district="Lunglei (669 Dataset Incidents)", state="Mizoram", flood_risk_pct=28.0, landslide_risk_pct=89.0, status="Critical", people_at_risk=890),
            DistrictRiskSummary(district="East Khasi Hills (405 Dataset Incidents)", state="Meghalaya", flood_risk_pct=42.0, landslide_risk_pct=92.0, status="Critical", people_at_risk=910),
            DistrictRiskSummary(district="Dima Hasao (387 Dataset Incidents)", state="Assam", flood_risk_pct=62.0, landslide_risk_pct=87.0, status="Critical", people_at_risk=810),
            DistrictRiskSummary(district="Kohima (487 Dataset Incidents)", state="Nagaland", flood_risk_pct=30.0, landslide_risk_pct=84.0, status="High", people_at_risk=650),
            DistrictRiskSummary(district="Ukhrul (315 Dataset Incidents)", state="Manipur", flood_risk_pct=24.0, landslide_risk_pct=78.0, status="High", people_at_risk=480),
            DistrictRiskSummary(district="Kamrup / Guwahati Basin", state="Assam", flood_risk_pct=85.0, landslide_risk_pct=48.0, status="High", people_at_risk=1250),
            DistrictRiskSummary(district="Goalpara", state="Assam", flood_risk_pct=90.0, landslide_risk_pct=52.0, status="High", people_at_risk=940)
        ]
        db.add_all(summaries)
        db.commit()
        logger.info("Seeded DistrictRiskSummaries from SIH26001 dataset.")

        # 5. System Alerts (Mapped from 11,026 SIH26001 Dataset Incidents)
        db.query(SystemAlert).delete()
        db.commit()

        alerts = [
            SystemAlert(
                alert_type="Landslide",
                title="Aizawl Slopes Failure Watch (1,317 Historical Slides Logged)",
                description="Extreme soil saturation on steep hill cuts along Aizawl-Lunglei highway corridor.",
                severity="Critical",
                time_ago="8 mins ago"
            ),
            SystemAlert(
                alert_type="Landslide",
                title="Shillong & Cherrapunji Slope Instability Alert (405 Historical Slides Logged)",
                description="Torrential rainfall causing active soil creep and rockfalls across East Khasi Hills.",
                severity="Critical",
                time_ago="22 mins ago"
            ),
            SystemAlert(
                alert_type="Flood",
                title="Brahmaputra Basin Surge near Kamrup & Goalpara",
                description="Water level exceeding warning marks along lower river basin; lowlands flooded.",
                severity="High",
                time_ago="45 mins ago"
            ),
            SystemAlert(
                alert_type="Landslide",
                title="Kohima NH-29 Debris Slide Watch (487 Historical Slides Logged)",
                description="Road excavation and monsoon runoff causing slope mass movement near Kohima town.",
                severity="High",
                time_ago="1 hr ago"
            ),
            SystemAlert(
                alert_type="Landslide",
                title="Dima Hasao Hill Sector Cut Failure (387 Historical Slides Logged)",
                description="Railway embankment and hill slope displacement reported in Dima Hasao district.",
                severity="High",
                time_ago="2 hrs ago"
            )
        ]
        db.add_all(alerts)
        db.commit()
        logger.info("Seeded SystemAlerts from SIH26001 dataset.")

        # 6. Risk Trends (7 days)
        if db.query(RiskTrend).count() == 0:
            trends = [
                RiskTrend(day_label="Mon", day_order=1, risk_value=45.0),
                RiskTrend(day_label="Tue", day_order=2, risk_value=58.0),
                RiskTrend(day_label="Wed", day_order=3, risk_value=64.0),
                RiskTrend(day_label="Thu", day_order=4, risk_value=78.0),
                RiskTrend(day_label="Fri", day_order=5, risk_value=72.0),
                RiskTrend(day_label="Sat", day_order=6, risk_value=88.0),
                RiskTrend(day_label="Sun", day_order=7, risk_value=94.0)
            ]
            db.add_all(trends)
            db.commit()
            logger.info("Seeded RiskTrends.")

        # 7. Action Recommendations
        if db.query(ActionRecommendation).count() == 0:
            recs = [
                ActionRecommendation(recommendation_text="Deploy emergency slope monitoring teams to high-density slide zones in Aizawl and Lunglei.", priority=1),
                ActionRecommendation(recommendation_text="Activate river-level monitoring and flood shelters in Goalpara and Kamrup embankments.", priority=2),
                ActionRecommendation(recommendation_text="Issue local SMS alerts to vulnerable hillside settlements in East Khasi Hills & Dima Hasao.", priority=3),
                ActionRecommendation(recommendation_text="Position heavy earthmoving clearing machinery along NH-29 Kohima corridor.", priority=4)
            ]
            db.add_all(recs)
            db.commit()
            logger.info("Seeded ActionRecommendations.")

        # 8. Volunteer Offers Seeding
        if db.query(VolunteerOffer).count() == 0:
            volunteers = [
                VolunteerOffer(
                    volunteer_name="Guwahati Relief Squad (Team Lead: Ankur Dutta)",
                    volunteer_phone="+91 98640 12345",
                    volunteer_email="ankur.relief@sathi.org",
                    help_type="Emergency Rescue & Medical Relief",
                    location_name="Guwahati Khanapara Slope Base",
                    latitude=26.1380,
                    longitude=91.7310,
                    message="Equipped with 2 relief vans, first-aid kits, and emergency ropes for slope evacuation.",
                    status="OFFERED"
                ),
                VolunteerOffer(
                    volunteer_name="Assam Youth Volunteers (Riya Sen)",
                    volunteer_phone="+91 97060 54321",
                    volunteer_email="riya.volunteers@gmail.com",
                    help_type="Food & Water Distribution",
                    location_name="Jorabat Relief Camp Station",
                    latitude=26.1790,
                    longitude=91.7480,
                    message="Distributing clean drinking water packets and 300 cooked meal packs for stranded families.",
                    status="ASSIGNED"
                ),
                VolunteerOffer(
                    volunteer_name="Dr. Sameer Baruah (Mobile Health Unit)",
                    volunteer_phone="+91 94350 99887",
                    volunteer_email="dr.baruah@medrelief.in",
                    help_type="Medical Assistance",
                    location_name="GS Road Medical Post",
                    latitude=26.1510,
                    longitude=91.7410,
                    message="Mobile ambulance and emergency trauma first aid kit ready for landslide injury support.",
                    status="OFFERED"
                )
            ]
            db.add_all(volunteers)
            db.commit()
            logger.info(f"Seeded {len(volunteers)} VolunteerOffers.")

    except Exception as err:
        logger.error(f"Error seeding initial database data: {err}")
        db.rollback()
