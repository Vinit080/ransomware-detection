import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from infra.database.database import get_db
from packages.security.rbac import RequireRole
from packages.schemas.models import SandboxRun, Sample, GenAIAnalysis, HeuristicScore

router = APIRouter()

@router.get("/export")
def export_metrics(
    format: Optional[str] = Query("json", description="Output format: json or csv"),
    db: Session = Depends(get_db),
    # Require RESEARCHER or ADMINISTRATOR role
    _ = Depends(RequireRole(["RESEARCHER", "ADMINISTRATOR"]))
):
    """
    Exports statistical metrics for all Sandbox Runs.
    Suitable for academic evaluation (Jupyter/pandas ingestion).
    """
    
    # We need to calculate flattened rows for each run
    runs = db.query(SandboxRun).all()
    
    export_data = []
    
    for run in runs:
        sample = run.sample
        
        # 1. Heuristics Aggregation
        heuristic_scores = db.query(HeuristicScore).filter(
            HeuristicScore.run_id == run.id,
            HeuristicScore.triggered == True
        ).all()
        cumulative_h_score = sum([h.contribution for h in heuristic_scores])
        
        # 2. GenAI Analysis
        ai_analysis = db.query(GenAIAnalysis).filter(GenAIAnalysis.run_id == run.id).order_by(GenAIAnalysis.id.desc()).first()
        
        ai_verdict = "UNKNOWN"
        ai_confidence = 0.0
        hallucination_detected = False
        
        if ai_analysis:
            ai_verdict = ai_analysis.output_json.get("verdict", "UNKNOWN") if ai_analysis.output_json else "UNKNOWN"
            ai_confidence = ai_analysis.confidence
            
            h_check = ai_analysis.hallucination_check
            if isinstance(h_check, dict):
                if h_check.get("status") == "failed":
                    hallucination_detected = True
                    
        row = {
            "run_id": run.id,
            "timestamp": run.started_at.isoformat() if run.started_at else "",
            "dataset_identifier": sample.sha256 if sample else "UNKNOWN",
            "sample_family": sample.family if sample else "UNKNOWN",
            "heuristic_cumulative_score": cumulative_h_score,
            "ai_verdict": ai_verdict,
            "ai_confidence_score": ai_confidence,
            "hallucination_detected": hallucination_detected
        }
        export_data.append(row)
        
    if format.lower() == "csv":
        if not export_data:
            return StreamingResponse(iter(["No data available"]), media_type="text/csv")
            
        stream = io.StringIO()
        csv_writer = csv.DictWriter(stream, fieldnames=export_data[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(export_data)
        
        response = Response(content=stream.getvalue(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=ransomshield_metrics.csv"
        return response
        
    return JSONResponse(content={"metrics": export_data})
