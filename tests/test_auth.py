import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from apps.api.main import app
from infra.database.database import get_db
from packages.schemas.models import Base, User
from packages.security.auth import get_password_hash

from sqlalchemy.pool import StaticPool

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
    # Create an admin user for testing
    admin = User(username="admin", hashed_password=get_password_hash("adminpass"), role="ADMINISTRATOR")
    db.add(admin)
    db.commit()
    yield
    Base.metadata.drop_all(bind=engine)

def test_login_success():
    response = client.post("/api/v1/auth/token", data={"username": "admin", "password": "adminpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/api/v1/auth/token", data={"username": "admin", "password": "wrongpass"})
    assert response.status_code == 401

def test_create_user_as_admin():
    # 1. Login as admin
    login_resp = client.post("/api/v1/auth/token", data={"username": "admin", "password": "adminpass"})
    token = login_resp.json()["access_token"]
    
    # 2. Create new user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/auth/users", 
        json={"username": "new_analyst", "password": "password123", "role": "ANALYST"},
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["username"] == "new_analyst"
    assert response.json()["role"] == "ANALYST"

def test_create_user_as_analyst_fails():
    # We just created 'new_analyst'. Let's login as them.
    login_resp = client.post("/api/v1/auth/token", data={"username": "new_analyst", "password": "password123"})
    token = login_resp.json()["access_token"]
    
    # Try to create another user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/auth/users", 
        json={"username": "hacker", "password": "password123", "role": "ADMINISTRATOR"},
        headers=headers
    )
    assert response.status_code == 403 # Forbidden!
