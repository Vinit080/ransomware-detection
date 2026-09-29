import pytest
import time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.main import app
from infra.database.database import get_db
from packages.schemas.models import Base, User, Sample, SandboxRun
from packages.security.auth import get_password_hash

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
    # Create researcher
    researcher = User(username="researcher_1", hashed_password=get_password_hash("password123"), role="RESEARCHER")
    db.add(researcher)
    # Create test sample
    sample = Sample(id="sample-1", sha256="fakehash123", family="TestFamily")
    db.add(sample)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def researcher_token():
    resp = client.post("/api/v1/auth/token", data={"username": "researcher_1", "password": "password123"})
    return resp.json()["access_token"]

def test_start_sandbox_run(researcher_token):
    headers = {"Authorization": f"Bearer {researcher_token}"}
    run_data = {
        "sample_sha256": "fakehash123",
        "vm_id": "test-vm-01",
        "snapshot_id": "snap-clean"
    }
    
    # 1. Start the run
    response = client.post("/api/v1/sandbox/runs", json=run_data, headers=headers)
    assert response.status_code == 201
    run_id = response.json()["id"]
    assert response.json()["status"] == "INITIALIZING"
    
    # 2. Polling the status endpoint to verify background execution
    # The mock hypervisor has time.sleeps totaling ~5 seconds for a full run.
    # We will poll up to 10 seconds.
    status = "INITIALIZING"
    for _ in range(10):
        time.sleep(1)
        resp = client.get(f"/api/v1/sandbox/runs/{run_id}", headers=headers)
        assert resp.status_code == 200
        status = resp.json()["status"]
        if status == "COMPLETED":
            break
            
    assert status == "COMPLETED"
    
    # Verify isolation status was verified
    resp = client.get(f"/api/v1/sandbox/runs/{run_id}", headers=headers)
    assert resp.json()["isolation_status"] == "VERIFIED"
