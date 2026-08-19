import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import psutil
import argparse
from typing import List, Dict, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from packages.schemas.models import TelemetryEvent, Base

# Import the engines
from services.analysis.heuristics.engine import HeuristicsEngine
from services.analysis.ai.engine import GenAIEngine

def setup_mock_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def calculate_metrics(results: List[Dict]) -> Dict:
    tp = sum(1 for r in results if r['ground_truth'] == 'MALICIOUS' and r['verdict'] == 'MALICIOUS')
    tn = sum(1 for r in results if r['ground_truth'] == 'BENIGN' and r['verdict'] == 'BENIGN')
    fp = sum(1 for r in results if r['ground_truth'] == 'BENIGN' and r['verdict'] == 'MALICIOUS')
    fn = sum(1 for r in results if r['ground_truth'] == 'MALICIOUS' and r['verdict'] == 'BENIGN')

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # ATT&CK Mapping Accuracy and Unsupported Claim Rate
    attck_hits = 0
    attck_total = 0
    unsupported_claims = 0
    total_claims = 0
    
    for r in results:
        if r['ground_truth'] == 'MALICIOUS':
            true_set = set(r['true_attck_techniques'])
            pred_set = set(r.get('predicted_attck_techniques', []))
            if true_set:
                attck_hits += len(true_set.intersection(pred_set))
                attck_total += len(true_set)
            
            unsupported_set = pred_set - true_set
            unsupported_claims += len(unsupported_set)
            total_claims += len(pred_set)
            
    attck_acc = attck_hits / attck_total if attck_total > 0 else 0.0
    unsupported_claim_rate = unsupported_claims / total_claims if total_claims > 0 else 0.0

    # Telemetry Tamper Detection
    tamper_ground_truth_count = sum(1 for r in results if r.get('telemetry_tampered_ground_truth', False))
    tamper_detections = sum(1 for r in results if r.get('telemetry_tampered_ground_truth', False) and r.get('telemetry_tampered', False))
    tamper_detection_rate = tamper_detections / tamper_ground_truth_count if tamper_ground_truth_count > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "attck_acc": attck_acc,
        "unsupported_claim_rate": unsupported_claim_rate,
        "telemetry_tamper_detection": tamper_detection_rate,
        "latency_ms": sum(r['latency_ms'] for r in results) / len(results) if results else 0.0,
        "cpu_overhead_percent": sum(r['cpu_overhead'] for r in results) / len(results) if results else 0.0,
        "memory_overhead_mb": sum(r['mem_overhead'] for r in results) / len(results) if results else 0.0
    }

import datetime

import uuid

def run_evaluation(dataset_path: str, use_genai: bool = False, active_simulation: bool = False):
    with open(dataset_path, 'r') as f:
        data = json.load(f)

    db = setup_mock_db()
    heuristics = HeuristicsEngine(db)
    genai = GenAIEngine(db) if use_genai else None

    results = []

    print(f"\n--- Running Evaluation: GenAI={use_genai}, ActiveSim={active_simulation} ---")
    
    for sample in data.get("samples", []):
        run_id = sample['id']
        
        # Load events into memory DB
        from packages.schemas.models import SandboxRun, Sample
        db.add(Sample(id=run_id, sha256=f"mock_{run_id}"))
        db.add(SandboxRun(id=run_id, sample_id=run_id, status="COMPLETED"))
        
        for ev in sample['events']:
            db.add(TelemetryEvent(
                id=str(uuid.uuid4()),
                run_id=run_id,
                event_type=ev['event_type'],
                timestamp=datetime.datetime.fromtimestamp(ev['timestamp']),
                event_data=ev['data']
            ))
        db.commit()

        # Measurement Start
        process = psutil.Process(os.getpid())
        start_cpu = process.cpu_percent()
        start_mem = process.memory_info().rss
        start_time = time.time()

        # Deterministic Baseline
        is_malicious = heuristics.analyze_run(run_id)
        predicted_attck = []

        # Simulated Active Network Responses
        if active_simulation:
            # Active simulation adds small delay and forces heuristics threshold lower
            time.sleep(0.05) 
            if not is_malicious and len(sample['events']) > 1:
                # Mock simulation exposing hidden behaviors
                is_malicious = True 

        # GenAI/RAG
        is_tampered = False
        if use_genai and is_malicious:
            try:
                genai.analyze_run(run_id)
                from packages.schemas.models import GenAIAnalysis
                analysis = db.query(GenAIAnalysis).filter(GenAIAnalysis.run_id == run_id).first()
                if analysis and analysis.output_json:
                    mappings = analysis.output_json.get("attck_mappings", [])
                    predicted_attck = [m.get("technique_id") for m in mappings]
                    is_tampered = analysis.output_json.get("telemetry_tampered", False)
            except Exception as e:
                pass

        # Measurement End
        end_time = time.time()
        end_cpu = process.cpu_percent()
        end_mem = process.memory_info().rss

        results.append({
            "id": run_id,
            "ground_truth": sample['ground_truth'],
            "verdict": "MALICIOUS" if is_malicious else "BENIGN",
            "true_attck_techniques": sample['true_attck_techniques'],
            "predicted_attck_techniques": predicted_attck,
            "telemetry_tampered_ground_truth": sample.get('telemetry_tampered_ground_truth', False),
            "telemetry_tampered": is_tampered,
            "latency_ms": (end_time - start_time) * 1000,
            "cpu_overhead": max(0, end_cpu - start_cpu),
            "mem_overhead": max(0, (end_mem - start_mem) / (1024 * 1024))
        })

    return calculate_metrics(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="benchmark_dataset.json", help="Path to empirical dataset")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Dataset {args.dataset} not found. Please create it first.")
        exit(1)

    print("Executing Authorised Controlled Runs for Table III...")
    
    # 1. Passive / Baseline (Deterministic Only)
    baseline = run_evaluation(args.dataset, use_genai=False, active_simulation=False)
    
    # 2. Deterministic + GenAI/RAG (Proposed)
    proposed = run_evaluation(args.dataset, use_genai=True, active_simulation=False)
    
    # Print Table III format
    print("\n" + "="*80)
    print("TABLE III: RESULT STRUCTURE TO BE POPULATED FROM CONTROLLED RUNS")
    print("="*80)
    print(f"{'Metric':<25} | {'Passive / Baseline':<20} | {'Proposed':<20} | {'Change':<10}")
    print("-" * 80)
    
    metrics_map = [
        ("Detection precision", "precision", True),
        ("Detection recall", "recall", True),
        ("F1 score", "f1", True),
        ("ATT&CK mapping accuracy", "attck_acc", True),
        ("Unsupported-claim rate", "unsupported_claim_rate", True),
        ("Telemetry tamper detection", "telemetry_tamper_detection", True),
        ("Median end-to-end latency", "latency_ms", False),
        ("CPU overhead (%)", "cpu_overhead_percent", False),
        ("Memory overhead (MB)", "memory_overhead_mb", False)
    ]
    
    for display_name, key, is_percent in metrics_map:
        val_base = baseline[key]
        val_prop = proposed[key]
        
        diff = val_prop - val_base
        if is_percent:
            b_str = f"{val_base:.2f}"
            p_str = f"{val_prop:.2f}"
            c_str = f"{diff:+.2f}"
        else:
            b_str = f"{val_base:.2f}"
            p_str = f"{val_prop:.2f}"
            c_str = f"{diff:+.2f}"
            
        print(f"{display_name:<25} | {b_str:<20} | {p_str:<20} | {c_str:<10}")
    
    print("="*80)
    print("Note: Run with an active Ollama endpoint and comprehensive dataset for valid results.")
