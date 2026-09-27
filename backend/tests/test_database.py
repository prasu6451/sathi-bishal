"""Unit tests for SQLAlchemy Database Repositories."""
import pytest
from app.database.connection import SessionLocal, init_db
from app.database.repositories import LocationRepository, RiskPredictionRepository, CitizenReportRepository


@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_and_query_location(db_session):
    repo = LocationRepository(db_session)
    loc = repo.create(name="Test Shillong Location", latitude=25.55, longitude=91.90)
    assert loc.id is not None
    assert loc.name == "Test Shillong Location"


def test_create_and_query_citizen_report(db_session):
    repo = CitizenReportRepository(db_session)
    rep = repo.create_report(lat=26.15, lon=91.75, severity=4, description="Hillside crack observed")
    assert rep.id is not None
    assert rep.severity == 4


def test_create_risk_prediction(db_session):
    repo = RiskPredictionRepository(db_session)
    pred = repo.create({
        "latitude": 26.15,
        "longitude": 91.75,
        "risk_probability": 0.85,
        "risk_score": 85,
        "risk_level": "CRITICAL",
        "model_version": "xgb-v1"
    })
    assert pred.id is not None
    assert pred.risk_level == "CRITICAL"
