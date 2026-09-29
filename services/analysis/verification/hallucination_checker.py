import logging
from sqlalchemy.orm import Session
from packages.schemas.models import GenAIAnalysis, AttckMapping, HeuristicScore

logger = logging.getLogger(__name__)

class HallucinationChecker:
    def __init__(self, db: Session):
        self.db = db
        # Map ATT&CK techniques to the required Heuristic Rule IDs
        self.technique_to_heuristic = {
            "T1490": ["RULE_001_VSSADMIN_DELETE", "RULE_003_BCDEDIT_NO_RECOVERY"], # Inhibit System Recovery
            "T1486": ["RULE_002_RAPID_ENTROPY"], # Data Encrypted for Impact
            "T1071": ["RULE_004_SUSPICIOUS_DNS"]  # Application Layer Protocol (C2)
        }
        
    def verify_run(self, run_id: str) -> bool:
        """
        Cross-references GenAI ATT&CK mappings against Heuristic Scores.
        Returns True if any hallucinations were detected, False otherwise.
        """
        logger.info(f"Starting Hallucination Checker for run {run_id}")
        
        # 1. Fetch GenAI Analysis
        ai_analysis = self.db.query(GenAIAnalysis).filter(GenAIAnalysis.run_id == run_id).first()
        if not ai_analysis:
            logger.warning(f"No GenAI analysis found for run {run_id}. Skipping verification.")
            return False
            
        # 2. Fetch ATT&CK Mappings
        mappings = self.db.query(AttckMapping).filter(AttckMapping.run_id == run_id).all()
        if not mappings:
            logger.info("No ATT&CK mappings to verify.")
            # Update check status to passed since no mappings were made to hallucinate
            ai_analysis.hallucination_check = {"status": "passed", "hallucinated_techniques": []}
            self.db.commit()
            return False
            
        # 3. Fetch Triggered Heuristics
        triggered_heuristics = self.db.query(HeuristicScore).filter(
            HeuristicScore.run_id == run_id, 
            HeuristicScore.triggered == True
        ).all()
        triggered_rule_ids = [h.rule_id for h in triggered_heuristics]
        
        hallucinated_techniques = []
        
        # 4. Cross-Reference
        for mapping in mappings:
            tech_id = mapping.technique_id
            
            if tech_id in self.technique_to_heuristic:
                required_rules = self.technique_to_heuristic[tech_id]
                
                # Check if AT LEAST ONE required heuristic was triggered
                is_supported = any(rule in triggered_rule_ids for rule in required_rules)
                
                if not is_supported:
                    logger.warning(f"Hallucination Detected! AI claimed {tech_id} but no supporting telemetry heuristic triggered.")
                    hallucinated_techniques.append(tech_id)
                    
                    # Penalize confidence score for this specific mapping
                    mapping.final_confidence = 0.0
                else:
                    # Verified mapping
                    mapping.final_confidence = mapping.genai_confidence
            else:
                # If we don't have a mathematical rule for this technique yet, we trust the AI
                # but might slightly penalize final_confidence for lack of hard evidence
                mapping.final_confidence = mapping.genai_confidence * 0.9
                
        # 5. Update GenAI Analysis Record
        is_hallucinated = len(hallucinated_techniques) > 0
        ai_analysis.hallucination_check = {
            "status": "failed" if is_hallucinated else "passed",
            "hallucinated_techniques": hallucinated_techniques
        }
        
        if is_hallucinated:
            # Penalize overall confidence of the AI analysis
            penalty = 0.15 * len(hallucinated_techniques)
            ai_analysis.confidence = max(0.0, ai_analysis.confidence - penalty)
            
        self.db.commit()
        
        logger.info(f"Verification complete. Hallucinations found: {is_hallucinated}")
        return is_hallucinated
