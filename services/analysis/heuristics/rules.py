from abc import ABC, abstractmethod
from typing import List
from packages.schemas.models import TelemetryEvent

class HeuristicRule(ABC):
    def __init__(self, rule_id: str, description: str, base_score: float):
        self.rule_id = rule_id
        self.description = description
        self.base_score = base_score

    @abstractmethod
    def evaluate(self, events: List[TelemetryEvent]) -> float:
        """
        Evaluates the telemetry dataset against the rule logic.
        Returns the calculated score contribution (0.0 if not triggered).
        """
        pass

class ShadowCopyDeletionRule(HeuristicRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE_001_VSSADMIN_DELETE",
            description="Detects execution of vssadmin or wmic to delete shadow volume copies",
            base_score=8.5
        )

    def evaluate(self, events: List[TelemetryEvent]) -> float:
        score = 0.0
        for event in events:
            if event.event_type == "process_creation" and event.event_data:
                cmdline = str(event.event_data.get("command_line", "")).lower()
                if "vssadmin" in cmdline and "delete shadows" in cmdline:
                    score += self.base_score
                elif "wmic" in cmdline and "shadowcopy delete" in cmdline:
                    score += self.base_score
        # Cap the score to avoid runaway additions if executed in a loop
        return min(score, self.base_score * 1.5)

class RapidEncryptionRule(HeuristicRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE_002_RAPID_ENTROPY",
            description="Detects rapid sequential file modifications with high entropy",
            base_score=7.0
        )

    def evaluate(self, events: List[TelemetryEvent]) -> float:
        high_entropy_count = 0
        for event in events:
            if event.event_type == "filesystem_entropy" and event.event_data:
                entropy = event.event_data.get("entropy", 0.0)
                if entropy > 7.5:
                    high_entropy_count += 1
        
        # Arbitrary threshold: if more than 5 high-entropy files, trigger
        if high_entropy_count >= 5:
            return self.base_score + (min(high_entropy_count - 5, 20) * 0.1)
        return 0.0

class BootConfigModificationRule(HeuristicRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE_003_BCDEDIT_NO_RECOVERY",
            description="Detects modification of boot config to disable recovery",
            base_score=9.0
        )

    def evaluate(self, events: List[TelemetryEvent]) -> float:
        for event in events:
            if event.event_type == "process_creation" and event.event_data:
                cmdline = str(event.event_data.get("command_line", "")).lower()
                if "bcdedit" in cmdline and "recoveryenabled no" in cmdline:
                    return self.base_score
        return 0.0

class DnsC2Rule(HeuristicRule):
    def __init__(self):
        super().__init__(
            rule_id="RULE_004_SUSPICIOUS_DNS",
            description="Detects DNS queries to potentially malicious domains (simulated list)",
            base_score=6.0
        )

    def evaluate(self, events: List[TelemetryEvent]) -> float:
        # In a real system, this would check against a Threat Intelligence DB.
        suspicious_keywords = ["malicious", "c2", "onion", "tor2web"]
        score = 0.0
        for event in events:
            if event.event_type == "dns_query" and event.event_data:
                query = str(event.event_data.get("query", "")).lower()
                for keyword in suspicious_keywords:
                    if keyword in query:
                        score += self.base_score
                        break
        return min(score, self.base_score * 2.0)
