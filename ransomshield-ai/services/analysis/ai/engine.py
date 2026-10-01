import os
import json
import hashlib
import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import ollama

from packages.schemas.models import SandboxRun, TelemetryEvent, GenAIAnalysis, AttckMapping

logger = logging.getLogger(__name__)

class GenAIEngine:
    def __init__(self, db: Session):
        self.db = db
        self.model_name = os.environ.get("OLLAMA_MODEL", "llama3") 

    def _summarize_telemetry(self, events: List[TelemetryEvent]) -> str:
        """
        Compresses and filters raw telemetry to prevent blowing up the LLM context window.
        """
        summary = []
        process_counts = {}
        high_entropy_files = 0
        dns_queries = []
        
        for event in events:
            if event.event_type == "process_creation" and event.event_data:
                cmd = event.event_data.get("command_line", "")
                if cmd:
                    process_counts[cmd] = process_counts.get(cmd, 0) + 1
                    
            elif event.event_type == "filesystem_entropy" and event.event_data:
                if event.event_data.get("entropy", 0.0) > 7.5:
                    high_entropy_files += 1
                    
            elif event.event_type == "dns_query" and event.event_data:
                query = event.event_data.get("query", "")
                if query and query not in dns_queries:
                    dns_queries.append(query)

        # Build concise JSON representation
        compressed_data = {
            "unique_commands_executed": list(process_counts.keys())[:20], # limit to first 20 unique commands
            "high_entropy_file_modifications": high_entropy_files,
            "unique_dns_queries": dns_queries[:10] # limit to 10 queries
        }
        
        return json.dumps(compressed_data)

    def _generate_prompt(self, compressed_telemetry: str) -> List[Dict[str, str]]:
        system_prompt = """
        You are an expert Principal Cybersecurity Analyst and Malware Reverse Engineer.
        Analyze the following compressed telemetry from a Windows sandbox environment.
        Determine if the behavior is MALICIOUS (specifically Ransomware) or BENIGN.
        Map any observed malicious behaviors to MITRE ATT&CK technique IDs (e.g., T1486 Data Encrypted for Impact, T1490 Inhibit System Recovery).
        
        You MUST respond ONLY with a valid JSON object matching this schema exactly:
        {
            "verdict": "MALICIOUS" | "BENIGN",
            "confidence": <float 0.0 to 1.0>,
            "reasoning": "Detailed technical explanation...",
            "telemetry_tampered": <boolean>,
            "attck_mappings": [
                {
                    "technique_id": "T1486",
                    "technique_name": "Data Encrypted for Impact"
                }
            ]
        }
        Do not include markdown blocks, just the raw JSON string.
        """
        return [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": f"Telemetry Data:\n{compressed_telemetry}"}
        ]

    def analyze_run(self, run_id: str) -> bool:
        logger.info(f"Starting GenAI Engine analysis for run {run_id}")
        
        run = self.db.query(SandboxRun).filter(SandboxRun.id == run_id).first()
        if not run:
            logger.error(f"SandboxRun {run_id} not found.")
            return False

        events = self.db.query(TelemetryEvent).filter(TelemetryEvent.run_id == run_id).order_by(TelemetryEvent.timestamp.asc()).all()
        if not events:
            logger.warning(f"No telemetry events found for run {run_id}")
            return False

        compressed_telemetry = self._summarize_telemetry(events)
        prompt = self._generate_prompt(compressed_telemetry)
        prompt_hash = hashlib.sha256(compressed_telemetry.encode()).hexdigest()
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=prompt,
                format='json'
            )
            
            raw_response = response['message']['content']
            parsed_json = json.loads(raw_response)
            
            # Save Analysis
            analysis = GenAIAnalysis(
                run_id=run_id,
                model=self.model_name,
                model_version="latest",
                prompt_version="v1.0",
                input_hash=prompt_hash,
                output_json=parsed_json,
                confidence=parsed_json.get("confidence", 0.0),
                hallucination_check={"status": "unchecked"}
            )
            self.db.add(analysis)
            
            # Save MITRE ATT&CK Mappings
            mappings = parsed_json.get("attck_mappings", [])
            for mapping in mappings:
                attck = AttckMapping(
                    run_id=run_id,
                    technique_id=mapping.get("technique_id"),
                    technique_name=mapping.get("technique_name"),
                    genai_confidence=parsed_json.get("confidence", 0.0)
                )
                self.db.add(attck)
                
            self.db.commit()
            
            verdict = parsed_json.get("verdict", "BENIGN")
            logger.info(f"GenAI Analysis complete. Verdict: {verdict}. ATT&CK Techniques: {len(mappings)}")
            
            return verdict == "MALICIOUS"
            
        except Exception as e:
            logger.error(f"Failed to execute GenAI analysis: {str(e)}")
            self.db.rollback()
            return False
