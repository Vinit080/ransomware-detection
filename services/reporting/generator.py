import os
import logging
import ollama
from sqlalchemy.orm import Session
from packages.schemas.models import SandboxRun, GenAIAnalysis, AttckMapping, Report

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.model_name = os.environ.get("OLLAMA_MODEL", "llama3")

    def _mock_cti_retrieval(self, technique_id: str) -> str:
        """
        Simulates retrieving mitigation contexts from a vector DB like pgvector based on ATT&CK IDs.
        """
        mock_cti_database = {
            "T1490": "Mitigation: Ensure Volume Shadow Copies are protected. Implement access controls to prevent standard processes from executing vssadmin.exe or wmic.exe.",
            "T1486": "Mitigation: Implement real-time file entropy monitoring and ransomware canaries. Ensure offline backups are maintained.",
            "T1071": "Mitigation: Implement strict egress filtering on Firewalls and analyze DNS logs for DGA and unauthorized C2 communication."
        }
        return mock_cti_database.get(technique_id, "No specific mitigation strategies found in CTI database.")

    def generate_report(self, run_id: str) -> bool:
        logger.info(f"Starting RAG Report Generation for run {run_id}")
        
        run = self.db.query(SandboxRun).filter(SandboxRun.id == run_id).first()
        if not run:
            logger.error(f"SandboxRun {run_id} not found.")
            return False

        analysis = self.db.query(GenAIAnalysis).filter(GenAIAnalysis.run_id == run_id).order_by(GenAIAnalysis.id.desc()).first()
        
        # Retrieve verified ATT&CK mappings (exclude hallucinated ones where final_confidence is 0.0)
        verified_mappings = self.db.query(AttckMapping).filter(
            AttckMapping.run_id == run_id,
            AttckMapping.final_confidence > 0.0
        ).all()
        
        # 1. RAG Retrieval Step
        cti_context = []
        for mapping in verified_mappings:
            mitigation = self._mock_cti_retrieval(mapping.technique_id)
            cti_context.append(f"- **{mapping.technique_id} ({mapping.technique_name})**: {mitigation}")
            
        cti_text = "\n".join(cti_context) if cti_context else "No verified ATT&CK techniques found."

        # 2. Prompt Construction
        system_prompt = """
        You are an expert Cybersecurity Incident Responder. 
        Generate a comprehensive Markdown report detailing the findings of a malware sandbox execution.
        Structure the report with the following sections:
        - Executive Summary
        - Technical Analysis & Verdict
        - MITRE ATT&CK Mapping
        - Mitigation Strategies
        
        Use the provided context to fill out the report. Do NOT hallucinate.
        """
        
        verdict = analysis.output_json.get("verdict", "UNKNOWN") if analysis else "UNKNOWN"
        reasoning = analysis.output_json.get("reasoning", "No AI reasoning provided.") if analysis else "N/A"
        
        user_context = f"""
        Sandbox Run ID: {run_id}
        Sample SHA256: {run.sample.sha256 if run.sample else 'UNKNOWN'}
        Final AI Verdict: {verdict}
        AI Reasoning: {reasoning}
        
        Retrieved Cyber Threat Intelligence (CTI) Context for Mitigations:
        {cti_text}
        """

        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_context.strip()}
        ]
        
        # 3. LLM Generation
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            report_content = response['message']['content']
            
            # 4. Persistence
            db_report = Report(
                run_id=run_id,
                report_type="Markdown",
                generated_content={"markdown": report_content},
                evidence_references={"cti_sources": [m.technique_id for m in verified_mappings]},
                generation_model=self.model_name
            )
            self.db.add(db_report)
            self.db.commit()
            
            logger.info("Successfully generated and saved Markdown report.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            self.db.rollback()
            return False
