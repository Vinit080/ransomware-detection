import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.schemas.models import Base, SandboxRun, Sample, GenAIAnalysis, AttckMapping, Report
from services.reporting.generator import ReportGenerator

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
    
    sample = Sample(id="test-sample-rep", sha256="hash_rep")
    run = SandboxRun(id="run-rep", sample_id="test-sample-rep", vm_id="vm1")
    
    # Fake Analysis
    analysis = GenAIAnalysis(
        run_id="run-rep", 
        confidence=0.9, 
        output_json={"verdict": "MALICIOUS", "reasoning": "Tested positive for Ransomware"}
    )
    
    # Verified Mapping
    mapping1 = AttckMapping(run_id="run-rep", technique_id="T1490", technique_name="Inhibit System Recovery", final_confidence=0.9)
    # Hallucinated Mapping
    mapping2 = AttckMapping(run_id="run-rep", technique_id="T1486", technique_name="Data Encrypted", final_confidence=0.0)
    
    db.add_all([sample, run, analysis, mapping1, mapping2])
    db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)

def test_report_generator():
    db = TestingSessionLocal()
    
    mock_response = {
        'message': {
            'content': "# Ransomware Report\n## Verdict\nMALICIOUS\n## Mitigations\nFix VSS."
        }
    }
    
    with patch("services.reporting.generator.ollama.chat", return_value=mock_response) as mock_chat:
        generator = ReportGenerator(db)
        success = generator.generate_report("run-rep")
        
        assert success == True
        
        # Verify db report
        report = db.query(Report).filter(Report.run_id == "run-rep").first()
        assert report is not None
        assert report.report_type == "Markdown"
        assert "Ransomware Report" in report.generated_content["markdown"]
        
        # Verify that only the verified technique (T1490) was used as evidence
        assert len(report.evidence_references["cti_sources"]) == 1
        assert "T1490" in report.evidence_references["cti_sources"]
        
        # Verify LLM was called with the context
        call_args = mock_chat.call_args[1]["messages"]
        user_prompt = call_args[1]["content"]
        assert "T1490" in user_prompt
        assert "T1486" not in user_prompt  # Because it was hallucinated
        assert "Tested positive" in user_prompt # Reasoning from analysis

    db.close()
