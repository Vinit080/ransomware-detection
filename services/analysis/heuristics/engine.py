import logging
from sqlalchemy.orm import Session
from packages.schemas.models import SandboxRun, TelemetryEvent, HeuristicScore
from .rules import (
    ShadowCopyDeletionRule,
    RapidEncryptionRule,
    BootConfigModificationRule,
    DnsC2Rule
)

logger = logging.getLogger(__name__)

class HeuristicsEngine:
    def __init__(self, db: Session):
        self.db = db
        self.rules = [
            ShadowCopyDeletionRule(),
            RapidEncryptionRule(),
            BootConfigModificationRule(),
            DnsC2Rule()
        ]
        # Threshold for final malicious verdict
        self.malicious_threshold = 10.0

    def analyze_run(self, run_id: str) -> bool:
        """
        Executes all heuristic rules against the telemetry for a given run_id.
        Returns True if the cumulative score exceeds the malicious threshold.
        """
        logger.info(f"Starting Heuristics Engine for run {run_id}")
        
        run = self.db.query(SandboxRun).filter(SandboxRun.id == run_id).first()
        if not run:
            logger.error(f"SandboxRun {run_id} not found.")
            return False

        # Retrieve all telemetry
        events = self.db.query(TelemetryEvent).filter(TelemetryEvent.run_id == run_id).all()
        if not events:
            logger.warning(f"No telemetry events found for run {run_id}")
            return False

        cumulative_score = 0.0
        
        for rule in self.rules:
            score = rule.evaluate(events)
            is_triggered = score > 0.0
            
            cumulative_score += score
            
            # Save the score
            h_score = HeuristicScore(
                run_id=run_id,
                rule_id=rule.rule_id,
                contribution=score,
                cumulative_score=cumulative_score,
                threshold=self.malicious_threshold,
                triggered=is_triggered
            )
            self.db.add(h_score)
            
            if is_triggered:
                logger.info(f"Rule {rule.rule_id} triggered with score {score}")

        self.db.commit()
        
        is_malicious = cumulative_score >= self.malicious_threshold
        logger.info(f"Heuristics completed. Cumulative Score: {cumulative_score}. Verdict: {'MALICIOUS' if is_malicious else 'BENIGN'}")
        
        return is_malicious
