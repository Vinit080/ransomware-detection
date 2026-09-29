import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.schemas.models import Base, TelemetryEvent, SandboxRun, Sample, HeuristicScore
from services.analysis.heuristics.engine import HeuristicsEngine

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create sample and run
    sample = Sample(id="test-sample-1", sha256="hash123")
    run = SandboxRun(id="run-100", sample_id="test-sample-1", vm_id="vm1")
    db.add_all([sample, run])
    db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)

def test_heuristics_engine():
    db = TestingSessionLocal()
    
    # 1. Create Malicious Telemetry
    events = []
    # Shadow Copy Deletion
    events.append(TelemetryEvent(
        id="evt-1", run_id="run-100", event_type="process_creation", 
        event_data={"command_line": "vssadmin.exe Delete Shadows /All /Quiet"}
    ))
    
    # Rapid Encryption (5 high entropy files)
    for i in range(5):
        events.append(TelemetryEvent(
            id=f"evt-e-{i}", run_id="run-100", event_type="filesystem_entropy",
            event_data={"entropy": 7.99}
        ))
        
    db.add_all(events)
    db.commit()
    
    # 2. Run Engine
    engine = HeuristicsEngine(db)
    is_malicious = engine.analyze_run("run-100")
    
    # 3. Verify
    # Vssadmin rule = 8.5
    # Rapid Encryption rule (5 files) = 7.0
    # Total = 15.5
    assert is_malicious == True
    
    # Check stored scores
    scores = db.query(HeuristicScore).filter(HeuristicScore.run_id == "run-100").all()
    assert len(scores) == 4 # 4 rules evaluated
    
    vss_score = next(s for s in scores if s.rule_id == "RULE_001_VSSADMIN_DELETE")
    assert vss_score.triggered == True
    assert vss_score.contribution == 8.5
    
    dns_score = next(s for s in scores if s.rule_id == "RULE_004_SUSPICIOUS_DNS")
    assert dns_score.triggered == False
    assert dns_score.contribution == 0.0
    
    db.close()
