import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.schemas.models import Base, SandboxRun, Sample, GenAIAnalysis, AttckMapping, HeuristicScore
from services.analysis.verification.hallucination_checker import HallucinationChecker

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
    
    # Create sample and runs
    sample = Sample(id="test-sample-hallu", sha256="hash_hallu")
    run_clean = SandboxRun(id="run-clean", sample_id="test-sample-hallu", vm_id="vm1")
    run_hallu = SandboxRun(id="run-hallu", sample_id="test-sample-hallu", vm_id="vm2")
    db.add_all([sample, run_clean, run_hallu])
    db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)

def test_hallucination_checker_no_hallucination():
    db = TestingSessionLocal()
    
    # AI Claims T1490
    analysis = GenAIAnalysis(run_id="run-clean", confidence=0.9, hallucination_check={})
    mapping = AttckMapping(run_id="run-clean", technique_id="T1490", genai_confidence=0.9)
    db.add_all([analysis, mapping])
    
    # Heuristics confirm RULE_001_VSSADMIN_DELETE
    h_score = HeuristicScore(run_id="run-clean", rule_id="RULE_001_VSSADMIN_DELETE", triggered=True, contribution=8.5)
    db.add(h_score)
    db.commit()
    
    checker = HallucinationChecker(db)
    is_hallucinated = checker.verify_run("run-clean")
    
    assert is_hallucinated == False
    
    # Verify DB
    db.refresh(analysis)
    assert analysis.hallucination_check["status"] == "passed"
    
    db.refresh(mapping)
    assert mapping.final_confidence == 0.9

def test_hallucination_checker_detects_hallucination():
    db = TestingSessionLocal()
    
    # AI Claims T1486 (Data Encrypted)
    analysis = GenAIAnalysis(run_id="run-hallu", confidence=0.8, hallucination_check={})
    mapping = AttckMapping(run_id="run-hallu", technique_id="T1486", genai_confidence=0.8)
    db.add_all([analysis, mapping])
    
    # Heuristics DO NOT confirm it (triggered=False)
    h_score = HeuristicScore(run_id="run-hallu", rule_id="RULE_002_RAPID_ENTROPY", triggered=False, contribution=0.0)
    db.add(h_score)
    db.commit()
    
    checker = HallucinationChecker(db)
    is_hallucinated = checker.verify_run("run-hallu")
    
    assert is_hallucinated == True
    
    # Verify DB
    db.refresh(analysis)
    assert analysis.hallucination_check["status"] == "failed"
    assert "T1486" in analysis.hallucination_check["hallucinated_techniques"]
    assert analysis.confidence < 0.8 # Confidence should be penalized
    
    db.refresh(mapping)
    assert mapping.final_confidence == 0.0 # Mapping confidence destroyed

    db.close()
