from typing import List, Dict

class RuleBasedMapper:
    def __init__(self):
        # A simple deterministic lookup mapper (S1 baseline)
        self.rules = {
            "vssadmin": "T1490",       # Inhibit System Recovery
            "wmic.exe shadowcopy": "T1490",
            "bcdedit": "T1490",
            "recoveryenabled no": "T1490",
            "powershell.exe -w hidden -enc": "T1059", # Command and Scripting Interpreter
            ".enc": "T1486",           # Data Encrypted for Impact
            "entropy": "T1486",
            "malicious-c2": "T1071"    # Application Layer Protocol
        }

    def analyze(self, events: List[Dict]) -> List[str]:
        predicted_techniques = set()
        
        for event in events:
            if event.get("event_type") == "process_creation":
                cmdline = event.get("data", {}).get("command_line", "").lower()
                for keyword, technique in self.rules.items():
                    if keyword in cmdline:
                        predicted_techniques.add(technique)
                        
            elif event.get("event_type") == "filesystem_entropy":
                filepath = event.get("data", {}).get("file_path", "").lower()
                entropy = event.get("data", {}).get("entropy", 0)
                if ".enc" in filepath or entropy > 7.5:
                    predicted_techniques.add("T1486")
                    
            elif event.get("event_type") == "dns_query":
                query = event.get("data", {}).get("query", "").lower()
                if "malicious-c2" in query:
                    predicted_techniques.add("T1071")
                    
        return list(predicted_techniques)

if __name__ == "__main__":
    mapper = RuleBasedMapper()
    events = [
        {"event_type": "process_creation", "data": {"command_line": "vssadmin.exe delete shadows /all /quiet"}},
        {"event_type": "filesystem_entropy", "data": {"entropy": 7.8, "file_path": "C:\\file.enc"}}
    ]
    print(f"Mapped techniques: {mapper.analyze(events)}")
