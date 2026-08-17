import json
from models.telemetry import TelemetryPayload
from services.yara_engine import yara_scanner
from services.ai_engine import ai_engine

class FusionEngine:
    def analyze_session(self, telemetry: TelemetryPayload) -> dict:
        """Fuses Rule-Based Engine and GenAI Engine outputs."""
        
        # 1. Rule-Based Engine (YARA)
        yara_results = yara_scanner.scan_telemetry(telemetry)
        
        # 2. GenAI Engine (RAG + Semantic Analysis)
        ai_results = ai_engine.analyze_telemetry(telemetry, yara_results)
        
        # 3. Fusion & Risk Assessment
        risk_score = 0
        if yara_results:
            risk_score += 50
            
        is_malicious = "malicious" in ai_results["analysis"].lower() or "ransomware" in ai_results["analysis"].lower()
        if is_malicious:
            risk_score += 50
            
        assessment = {
            "session_id": telemetry.session_id,
            "risk_score": min(risk_score, 100),
            "threat_level": "CRITICAL" if risk_score > 75 else "HIGH" if risk_score > 50 else "LOW",
            "rule_based_findings": yara_results,
            "genai_analysis": ai_results["analysis"],
            "rag_context_used": ai_results["retrieved_context"]
        }
        
        return assessment

fusion_engine = FusionEngine()
