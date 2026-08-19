import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.main import app
from infra.database.database import get_db
from packages.schemas.models import Base, User
from packages.security.auth import get_password_hash

# Create a clean in-memory sqlite for tests
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
    # Create an analyst user for testing sample registration
    analyst = User(username="analyst_1", hashed_password=get_password_hash("password123"), role="ANALYST")
    db.add(analyst)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def analyst_token():
    resp = client.post("/api/v1/auth/token", data={"username": "analyst_1", "password": "password123"})
    return resp.json()["access_token"]

def test_register_sample_success(analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    sample_data = {
        "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "family": "WannaCry",
        "variant": "v1.0",
        "source": "VirusTotal",
        "risk_classification": "High"
    }
    response = client.post("/api/v1/samples/", json=sample_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["sha256"] == "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    assert data["family"] == "WannaCry"
    assert "id" in data

def test_register_duplicate_sample_fails(analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    sample_data = {
        "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "family": "WannaCry",
    }
    response = client.post("/api/v1/samples/", json=sample_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Sample with this SHA-256 already exists"

def test_get_sample_by_hash(analyst_token):
    headers = {"Authorization": f"Bearer {analyst_token}"}
    response = client.get("/api/v1/samples/5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", headers=headers)
    assert response.status_code == 200
    assert response.json()["family"] == "WannaCry"

def test_unauthorized_access():
    response = client.get("/api/v1/samples/")
    assert response.status_code == 401
