import uuid
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from packages.schemas.models import SandboxRun, Sample
from .hypervisor.base import HypervisorAdapter

logger = logging.getLogger(__name__)

class SandboxOrchestrator:
    def __init__(self, db: Session, hypervisor: HypervisorAdapter):
        self.db = db
        self.hypervisor = hypervisor

    def start_execution(self, sample_sha256: str, vm_id: str, snapshot_id: str) -> str:
        """
        Begins the 19-step master execution lifecycle for a sample.
        Returns the created SandboxRun ID.
        """
        # 2. Verify authorised sample
        sample = self.db.query(Sample).filter(Sample.sha256 == sample_sha256).first()
        if not sample:
            raise ValueError("Sample not found or unauthorized")

        # 4. Create experiment ID / Run ID
        run_id = str(uuid.uuid4())
        run = SandboxRun(
            id=run_id,
            sample_id=sample.id,
            vm_id=vm_id,
            snapshot_id=snapshot_id,
            status="INITIALIZING",
            isolation_status="UNVERIFIED"
        )
        self.db.add(run)
        self.db.commit()

        # In a real environment, the rest of this function would be handed off 
        # to a background task (like Celery) so the API doesn't block.
        # For Phase 4, we will execute it synchronously or via FastAPI BackgroundTasks.
        return run_id

    def execute_lifecycle(self, run_id: str):
        """
        The background process that executes the actual Sandbox Lifecycle.
        """
        run = self.db.query(SandboxRun).filter(SandboxRun.id == run_id).first()
        if not run:
            logger.error(f"SandboxRun {run_id} not found")
            return

        try:
            # 1. Verify lab isolation
            if not self.hypervisor.verify_isolation(run.vm_id):
                raise Exception("Lab Isolation Verification Failed")
            run.isolation_status = "VERIFIED"
            self.db.commit()

            # 3. Verify clean VM snapshot
            # 17. Restore clean snapshot (we do it before starting as well for safety)
            self.hypervisor.revert_to_snapshot(run.vm_id, run.snapshot_id)

            # 5. Start telemetry collectors (Stub for Phase 5)
            logger.info(f"Starting host-side telemetry listener for run {run_id}")

            # 6. Start out-of-band network monitoring
            logger.info(f"Starting network monitor agent on host for VM {run.vm_id}")
            import subprocess
            net_monitor_process = subprocess.Popen(["python", "agents/host_side/network_monitor.py", "--url", "http://localhost:8000/api/v1/telemetry/ingest", "--run-id", run_id])

            # 7. Start optional controlled vulnerability simulation (Stub for Phase 10)

            # 8. Transfer sample to isolated guest
            self.hypervisor.start_vm(run.vm_id)
            # Assuming mock path for sample transfer
            self.hypervisor.transfer_file_to_guest(run.vm_id, "/mnt/storage/sample.exe", "C:\\Users\\Admin\\Desktop\\sample.exe")

            # 9. Execute sample
            run.status = "RUNNING"
            self.db.commit()
            self.hypervisor.execute_command_in_guest(run.vm_id, "C:\\Users\\Admin\\Desktop\\sample.exe")

            # 10. Stream telemetry (Stub for Phase 5 & 8)
            # 11. Stop execution based on policy or timeout
            import time
            time.sleep(10) # Simulate runtime
            self.hypervisor.stop_vm(run.vm_id)

            # 12. Flush telemetry
            if net_monitor_process:
                net_monitor_process.terminate()
                net_monitor_process.wait(timeout=5)
            
            # 13. Verify cryptographic integrity (Stub for Phase 8)
            
            run.status = "ANALYZING"
            self.db.commit()

            # 14. Run heuristic engine (Stub for Phase 7)
            from services.analysis.heuristics.engine import HeuristicsEngine
            heuristics = HeuristicsEngine(self.db)
            heuristics.analyze_run(run_id)

            # 15. Run GenAI/RAG analysis (Stub for Phase 9 & 10)
            from services.analysis.ai.engine import GenAIEngine
            from services.analysis.verification.hallucination_checker import HallucinationChecker
            
            ai_engine = GenAIEngine(self.db)
            ai_engine.analyze_run(run_id)
            
            checker = HallucinationChecker(self.db)
            checker.verify_run(run_id)

            # 16. Generate report (Stub for Phase 16)
            from services.reporting.generator import ReportGenerator
            report_gen = ReportGenerator(self.db)
            report_gen.generate_report(run_id)

            # 17. Restore clean snapshot
            self.hypervisor.revert_to_snapshot(run.vm_id, run.snapshot_id)

            # 18. Mark experiment complete
            run.status = "COMPLETED"
            run.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}")
            run.status = "FAILED"
            run.ended_at = datetime.now(timezone.utc)
            self.db.commit()
            # Attempt emergency stop
            self.hypervisor.stop_vm(run.vm_id)
