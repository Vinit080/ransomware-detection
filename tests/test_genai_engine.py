import json
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from packages.schemas.models import Base, TelemetryEvent, SandboxRun, Sample, GenAIAnalysis, AttckMapping
from services.analysis.ai.engine import GenAIEngine

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
    sample = Sample(id="test-sample-ai", sha256="hash_ai")
    run = SandboxRun(id="run-ai", sample_id="test-sample-ai", vm_id="vm1")
    db.add_all([sample, run])
    db.commit()
    
    yield
    Base.metadata.drop_all(bind=engine)

def test_genai_engine_analysis(monkeypatch):
    db = TestingSessionLocal()
    
    # Add fake telemetry
    events = [
        TelemetryEvent(
            id="evt-ai-1", run_id="run-ai", event_type="process_creation",
            event_data={"command_line": "vssadmin.exe Delete Shadows"}
        ),
        TelemetryEvent(
            id="evt-ai-2", run_id="run-ai", event_type="dns_query",
            event_data={"query": "malicious-c2.com"}
        )
    ]
    db.add_all(events)
    db.commit()

    # Mock the ollama response
    mock_json_reply = {
        "verdict": "MALICIOUS",
        "confidence": 0.95,
        "reasoning": "Deleted shadow copies and contacted C2.",
        "attck_mappings": [
            {
                "technique_id": "T1490",
                "technique_name": "Inhibit System Recovery"
            },
            {
                "technique_id": "T1071",
                "technique_name": "Application Layer Protocol"
            }
        ]
    }
    mock_response = {
        'message': {
            'content': json.dumps(mock_json_reply)
        }
    }
    
    # Patch ollama.chat
    with patch("services.analysis.ai.engine.ollama.chat", return_value=mock_response):
        ai_engine = GenAIEngine(db)
        is_malicious = ai_engine.analyze_run("run-ai")
        
        # Verify result
        assert is_malicious == True
        
        # Verify db models were created
        analysis = db.query(GenAIAnalysis).filter(GenAIAnalysis.run_id == "run-ai").first()
        assert analysis is not None
        assert analysis.confidence == 0.95
        assert analysis.output_json["verdict"] == "MALICIOUS"
        
        mappings = db.query(AttckMapping).filter(AttckMapping.run_id == "run-ai").all()
        assert len(mappings) == 2
        tech_ids = [m.technique_id for m in mappings]
        assert "T1490" in tech_ids
        assert "T1071" in tech_ids

    db.close()
