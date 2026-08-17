import yara
import json
import os
from models.telemetry import TelemetryPayload

class YaraEngine:
    def __init__(self, rules_path: str = "rules"):
        self.rules_path = rules_path
        self.rules = self._compile_rules()

    def _compile_rules(self):
        rule_files = {}
        if os.path.exists(self.rules_path):
            for filename in os.listdir(self.rules_path):
                if filename.endswith(".yar") or filename.endswith(".yara"):
                    rule_files[filename] = os.path.join(self.rules_path, filename)
        
        if rule_files:
            return yara.compile(filepaths=rule_files)
        return None

    def scan_telemetry(self, telemetry: TelemetryPayload) -> list:
        if not self.rules:
            return []
        
        # Serialize telemetry to JSON string for YARA to scan
        telemetry_json = telemetry.model_dump_json()
        
        # Scan the string buffer
        matches = self.rules.match(data=telemetry_json)
        
        results = []
        for match in matches:
            results.append({
                "rule": match.rule,
                "meta": match.meta,
                "tags": match.tags,
                "strings": [s[2].decode('utf-8', errors='ignore') for s in match.strings]
            })
        
        # Custom logic for complex JSON matching that YARA isn't perfect for
        self._custom_telemetry_heuristics(telemetry, results)
        
        return results

    def _custom_telemetry_heuristics(self, telemetry: TelemetryPayload, results: list):
        """Add heuristic checks that are easier in python than YARA over JSON."""
        # 1. Mass File Encryption Heuristic
        high_entropy_files = sum(1 for f in telemetry.files if f.entropy and f.entropy > 7.5)
        if high_entropy_files > 5:
            results.append({
                "rule": "Heuristic_Mass_High_Entropy",
                "meta": {"description": "Detected multiple files with very high entropy (>7.5)", "severity": "High"},
                "strings": []
            })
        
        # 2. Suspicious C2 Network
        for net in telemetry.networks:
            if net.destination_port in [4444, 9001, 8080]: # common shell/c2 ports
                results.append({
                    "rule": "Heuristic_Suspicious_Port",
                    "meta": {"description": f"Connection to suspicious port {net.destination_port}", "severity": "Medium"},
                    "strings": [str(net.destination_port)]
                })

# Global instance
yara_scanner = YaraEngine()
