from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from infra.database.database import get_db
from packages.schemas.models import User, SandboxRun, Report
from packages.security.rbac import RequireRole
from services.sandbox_orchestrator.orchestrator import SandboxOrchestrator
from services.sandbox_orchestrator.hypervisor.mock import MockHypervisorAdapter

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

sandbox_roles = RequireRole(["RESEARCHER", "ADMINISTRATOR"])

class SandboxRunCreate(BaseModel):
    sample_sha256: str
    vm_id: str
    snapshot_id: str
    configuration: Dict[str, Any] = {}

class SandboxRunResponse(BaseModel):
    id: str
    sample_id: str
    vm_id: str
    status: str
    isolation_status: str

    model_config = {"from_attributes": True}

@router.post("/runs", response_model=SandboxRunResponse, status_code=status.HTTP_201_CREATED)
def start_sandbox_run(
    run_in: SandboxRunCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(sandbox_roles)
):
    """
    Initiate a sandbox execution run for a given sample.
    Requires RESEARCHER or ADMINISTRATOR role.
    """
    # For Phase 4, we use the MockHypervisorAdapter
    hypervisor = MockHypervisorAdapter()
    orchestrator = SandboxOrchestrator(db, hypervisor)
    
    try:
        run_id = orchestrator.start_execution(run_in.sample_sha256, run_in.vm_id, run_in.snapshot_id)
        
        # Fire off the execution lifecycle in the background
        background_tasks.add_task(orchestrator.execute_lifecycle, run_id)
        
        # Retrieve and return the initialized run
        run = db.query(SandboxRun).filter(SandboxRun.id == run_id).first()
        return run
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/runs/{run_id}", response_model=SandboxRunResponse)
def get_sandbox_run_status(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(sandbox_roles)
):
    """
    Get the status of an ongoing or completed sandbox run.
    """
    run = db.query(SandboxRun).filter(SandboxRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@router.get("/runs/{run_id}/report")
def get_sandbox_run_report(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(sandbox_roles)
):
    """
    Retrieve the LLM generated markdown report for a completed run.
    """
    report = db.query(Report).filter(Report.run_id == run_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return {
        "run_id": report.run_id,
        "markdown": report.generated_content.get("markdown", "No markdown available.") if report.generated_content else "No content available.",
        "cti_references": report.generated_content.get("cti_references", []) if report.generated_content else []
    }
