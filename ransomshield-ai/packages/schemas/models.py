from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False) # e.g. ANALYST, RESEARCHER, ADMINISTRATOR
    is_active = Column(Boolean, default=True)

class Sample(Base):
    __tablename__ = "samples"
    
    id = Column(String, primary_key=True, index=True) # UUID or similar string
    sha256 = Column(String, unique=True, index=True, nullable=False)
    family = Column(String, index=True)
    variant = Column(String)
    source = Column(String)
    acquisition_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    authorisation_status = Column(String)
    risk_classification = Column(String)
    notes = Column(Text)

    runs = relationship("SandboxRun", back_populates="sample")

class SandboxRun(Base):
    __tablename__ = "sandbox_runs"

    id = Column(String, primary_key=True, index=True)
    sample_id = Column(String, ForeignKey("samples.id"), nullable=False)
    vm_id = Column(String)
    snapshot_id = Column(String)
    configuration = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    status = Column(String, index=True)
    isolation_status = Column(String)
    analyst_id = Column(String)

    sample = relationship("Sample", back_populates="runs")
    telemetry_events = relationship("TelemetryEvent", back_populates="run")
    behavioural_features = relationship("BehaviouralFeature", back_populates="run")
    heuristic_scores = relationship("HeuristicScore", back_populates="run")
    genai_analyses = relationship("GenAIAnalysis", back_populates="run")
    attck_mappings = relationship("AttckMapping", back_populates="run")
    reports = relationship("Report", back_populates="run")

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id = Column(String, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("sandbox_runs.id"), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    source = Column(String) # e.g., process, file, network
    event_type = Column(String, index=True)
    process_id = Column(Integer)
    parent_process_id = Column(Integer)
    process_name = Column(String)
    file_path = Column(String)
    destination_ip = Column(String)
    destination_port = Column(Integer)
    protocol = Column(String)
    severity = Column(String)
    raw_event_hash = Column(String)
    encrypted_payload_reference = Column(String)
    event_data = Column(JSON)

    run = relationship("SandboxRun", back_populates="telemetry_events")

class BehaviouralFeature(Base):
    __tablename__ = "behavioural_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("sandbox_runs.id"), nullable=False)
    feature_name = Column(String, index=True)
    feature_value = Column(JSON)
    confidence = Column(Float)
    source_events = Column(JSON) # List of event IDs

    run = relationship("SandboxRun", back_populates="behavioural_features")

class HeuristicScore(Base):
    __tablename__ = "heuristic_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("sandbox_runs.id"), nullable=False)
    rule_id = Column(String, index=True)
    contribution = Column(Float)
    cumulative_score = Column(Float)
    threshold = Column(Float)
    triggered = Column(Boolean, default=False)

    run = relationship("SandboxRun", back_populates="heuristic_scores")

class GenAIAnalysis(Base):
    __tablename__ = "genai_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("sandbox_runs.id"), nullable=False)
    model = Column(String)
    model_version = Column(String)
    prompt_version = Column(String)
    input_hash = Column(String)
    retrieved_context_ids = Column(JSON) # List of chunk IDs
    output_json = Column(JSON)
    confidence = Column(Float)
    hallucination_check = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("SandboxRun", back_populates="genai_analyses")

class AttckMapping(Base):
    __tablename__ = "attck_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("sandbox_runs.id"), nullable=False)
    technique_id = Column(String, index=True)
    technique_name = Column(String)
    evidence_event_ids = Column(JSON) # List of event IDs
    heuristic_confidence = Column(Float)
    genai_confidence = Column(Float)
    final_confidence = Column(Float)

    run = relationship("SandboxRun", back_populates="attck_mappings")

class Experiment(Base):
    __tablename__ = "experiments"

    experiment_id = Column(String, primary_key=True, index=True)
    experiment_type = Column(String, index=True)
    baseline = Column(String)
    configuration = Column(JSON)
    repetitions = Column(Integer)
    hardware_profile = Column(String)
    dataset_version = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    metrics = relationship("ExperimentMetric", back_populates="experiment")

class ExperimentMetric(Base):
    __tablename__ = "experiment_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String, ForeignKey("experiments.experiment_id"), nullable=False)
    metric_name = Column(String, index=True)
    metric_value = Column(Float)
    unit = Column(String)
    confidence_interval = Column(JSON) # [lower, upper]
    standard_deviation = Column(Float)

    experiment = relationship("Experiment", back_populates="metrics")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey("sandbox_runs.id"), nullable=False)
    report_type = Column(String)
    generated_content = Column(JSON)
    evidence_references = Column(JSON)
    generation_model = Column(String)
    generation_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    run = relationship("SandboxRun", back_populates="reports")
