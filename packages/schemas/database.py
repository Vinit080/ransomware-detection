import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Sample(Base):
    __tablename__ = 'samples'
    id = Column(String, primary_key=True, index=True) # UUID
    sha256 = Column(String(64), unique=True, index=True, nullable=False)
    family = Column(String, nullable=True)
    variant = Column(String, nullable=True)
    source = Column(String, nullable=True)
    acquisition_date = Column(DateTime(timezone=True), default=func.now())
    licence_status = Column(String, nullable=True)
    risk_classification = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    runs = relationship("SandboxRun", back_populates="sample")

class SandboxRun(Base):
    __tablename__ = 'sandbox_runs'
    id = Column(String, primary_key=True, index=True) # UUID
    sample_id = Column(String, ForeignKey('samples.id'), nullable=False)
    vm_id = Column(String, nullable=True)
    snapshot_id = Column(String, nullable=True)
    configuration = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="INITIALIZING") # INITIALIZING, RUNNING, COMPLETED, FAILED
    isolation_status = Column(String, default="VERIFIED")
    analyst_id = Column(String, nullable=True)

    sample = relationship("Sample", back_populates="runs")
    telemetry_events = relationship("TelemetryEvent", back_populates="run")
    heuristic_scores = relationship("HeuristicScore", back_populates="run")
    genai_analyses = relationship("GenAIAnalysis", back_populates="run")
    attck_mappings = relationship("AttckMapping", back_populates="run")

class TelemetryEvent(Base):
    __tablename__ = 'telemetry_events'
    id = Column(String, primary_key=True, index=True) # UUID
    run_id = Column(String, ForeignKey('sandbox_runs.id'), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    source = Column(String, nullable=False) # PROCESS, FILE, NETWORK
    event_type = Column(String, nullable=False)
    process_id = Column(Integer, nullable=True)
    parent_process_id = Column(Integer, nullable=True)
    process_name = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    destination_ip = Column(String, nullable=True)
    destination_port = Column(Integer, nullable=True)
    protocol = Column(String, nullable=True)
    severity = Column(String, nullable=True)
    raw_event_hash = Column(String, nullable=True)
    encrypted_payload_reference = Column(String, nullable=True)

    run = relationship("SandboxRun", back_populates="telemetry_events")

class HeuristicScore(Base):
    __tablename__ = 'heuristic_scores'
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('sandbox_runs.id'), nullable=False)
    rule_id = Column(String, nullable=False)
    contribution = Column(Float, nullable=False)
    cumulative_score = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    triggered = Column(Boolean, default=False)

    run = relationship("SandboxRun", back_populates="heuristic_scores")

class GenAIAnalysis(Base):
    __tablename__ = 'genai_analyses'
    id = Column(String, primary_key=True, index=True) # UUID
    run_id = Column(String, ForeignKey('sandbox_runs.id'), nullable=False)
    model = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    prompt_version = Column(String, nullable=False)
    input_hash = Column(String, nullable=True)
    retrieved_context_ids = Column(JSON, nullable=True) # List of chunk IDs
    output_json = Column(JSON, nullable=False)
    confidence = Column(Float, nullable=True)
    hallucination_check = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())

    run = relationship("SandboxRun", back_populates="genai_analyses")

class AttckMapping(Base):
    __tablename__ = 'attck_mappings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String, ForeignKey('sandbox_runs.id'), nullable=False)
    technique_id = Column(String, nullable=False)
    technique_name = Column(String, nullable=False)
    evidence_event_ids = Column(JSON, nullable=True) # List of telemetry event UUIDs
    heuristic_confidence = Column(Float, nullable=True)
    genai_confidence = Column(Float, nullable=True)
    final_confidence = Column(Float, nullable=True)

    run = relationship("SandboxRun", back_populates="attck_mappings")

class Experiment(Base):
    __tablename__ = 'experiments'
    experiment_id = Column(String, primary_key=True, index=True) # UUID
    experiment_type = Column(String, nullable=False)
    baseline = Column(String, nullable=False)
    configuration = Column(JSON, nullable=False)
    repetitions = Column(Integer, default=1)
    hardware_profile = Column(String, nullable=True)
    dataset_version = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    metrics = relationship("ExperimentMetric", back_populates="experiment")

class ExperimentMetric(Base):
    __tablename__ = 'experiment_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(String, ForeignKey('experiments.experiment_id'), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    confidence_interval = Column(String, nullable=True)
    standard_deviation = Column(Float, nullable=True)

    experiment = relationship("Experiment", back_populates="metrics")

class Report(Base):
    __tablename__ = 'reports'
    id = Column(String, primary_key=True, index=True) # UUID
    run_id = Column(String, ForeignKey('sandbox_runs.id'), nullable=False)
    report_type = Column(String, nullable=False)
    generated_content = Column(Text, nullable=False)
    evidence_references = Column(JSON, nullable=True)
    generation_model = Column(String, nullable=True)
    generation_timestamp = Column(DateTime(timezone=True), default=func.now())
