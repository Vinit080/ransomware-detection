import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from packages.schemas.models import Base, Sample, SandboxRun

@pytest.fixture(scope="module")
def db_session():
    # Use in-memory SQLite for testing model creation
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_sample(db_session):
    sample = Sample(id="uuid-1", sha256="abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234")
    db_session.add(sample)
    db_session.commit()
    
    retrieved = db_session.query(Sample).filter_by(id="uuid-1").first()
    assert retrieved is not None
    assert retrieved.sha256 == "abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234abcd1234"

def test_create_sandbox_run(db_session):
    run = SandboxRun(id="run-1", sample_id="uuid-1", vm_id="vm-01")
    db_session.add(run)
    db_session.commit()

    retrieved = db_session.query(SandboxRun).filter_by(id="run-1").first()
    assert retrieved is not None
    assert retrieved.vm_id == "vm-01"
