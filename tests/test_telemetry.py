import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.main import app
from infra.database.database import get_db
from packages.schemas.models import Base, TelemetryEvent

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
    yield
    Base.metadata.drop_all(bind=engine)

def test_ingest_telemetry_batch():
    run_id = "test-run-id-1234"
    events = [
        {
            "run_id": run_id,
            "event_type": "filesystem_entropy",
            "process_id": 4512,
            "process_name": "malware.exe",
            "event_data": {
                "action": "FILE_MODIFIED",
                "file_path": "C:\\Users\\Public\\secret.txt",
                "entropy": 7.99
            }
        },
        {
            "run_id": run_id,
            "event_type": "api_hook",
            "process_id": 4512,
            "process_name": "malware.exe",
            "event_data": {
                "api": "CryptEncrypt",
                "library": "advapi32.dll"
            }
        }
    ]
    
    response = client.post("/api/v1/telemetry/ingest", json=events)
    assert response.status_code == 202
    assert response.json() == {"detail": "Ingested 2 events"}
    
    # Verify events are in the database
    db = TestingSessionLocal()
    db_events = db.query(TelemetryEvent).filter(TelemetryEvent.run_id == run_id).all()
    assert len(db_events) == 2
    
    entropy_event = next(e for e in db_events if e.event_type == "filesystem_entropy")
    assert entropy_event.event_data["entropy"] == 7.99
    
    db.close()
