import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone

from apps.api.main import app
from infra.database.database import get_db
from packages.schemas.models import Base, User, SandboxRun, Sample, GenAIAnalysis, HeuristicScore
from packages.security.auth import create_access_token

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create test user (RESEARCHER)
    user = User(username="researcher", hashed_password="fake", role="RESEARCHER")
    
    # Create Sample and Run
    sample = Sample(id="test-sample-met", sha256="hash_met", family="WannaCry")
    run = SandboxRun(id="run-met", sample_id="test-sample-met", vm_id="vm1", started_at=datetime.now(timezone.utc))
    
    # Add Heuristics and Analysis
    h_score = HeuristicScore(run_id="run-met", rule_id="RULE_001_VSSADMIN_DELETE", triggered=True, contribution=8.5)
    analysis = GenAIAnalysis(
        run_id="run-met", 
        confidence=0.8, 
        output_json={"verdict": "MALICIOUS"},
        hallucination_check={"status": "failed"} # Simulating hallucinated
    )
    
    db.add_all([user, sample, run, h_score, analysis])
    db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)

def get_auth_headers():
    token = create_access_token(data={"sub": "researcher", "role": "RESEARCHER"})
    return {"Authorization": f"Bearer {token}"}

def test_export_metrics_json():
    response = client.get("/api/v1/metrics/export?format=json", headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert len(data["metrics"]) == 1
    
    row = data["metrics"][0]
    assert row["run_id"] == "run-met"
    assert row["sample_family"] == "WannaCry"
    assert row["heuristic_cumulative_score"] == 8.5
    assert row["ai_verdict"] == "MALICIOUS"
    assert row["ai_confidence_score"] == 0.8
    assert row["hallucination_detected"] == True

def test_export_metrics_csv():
    response = client.get("/api/v1/metrics/export?format=csv", headers=get_auth_headers())
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    
    csv_data = response.text
    assert "run_id,timestamp,dataset_identifier" in csv_data
    assert "run-met" in csv_data
    assert "WannaCry" in csv_data
    assert "8.5" in csv_data
    assert "MALICIOUS" in csv_data
    assert "True" in csv_data
