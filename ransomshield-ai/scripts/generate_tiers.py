import json
import random
import uuid

def generate_benign_event(timestamp_base, ambiguous=False):
    events = [
        {"event_type": "process_creation", "timestamp": timestamp_base, "data": {"command_line": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"}},
        {"event_type": "dns_query", "timestamp": timestamp_base + 1, "data": {"query": "google.com"}},
    ]
    if ambiguous:
        events.append({"event_type": "process_creation", "timestamp": timestamp_base + 2, "data": {"command_line": "vssadmin.exe list shadows"}})
        events.append({"event_type": "filesystem_entropy", "timestamp": timestamp_base + 3, "data": {"entropy": random.uniform(6.5, 7.2), "file_path": "C:\\Users\\admin\\Documents\\archive.zip"}})
    else:
        events.append({"event_type": "filesystem_entropy", "timestamp": timestamp_base + 3, "data": {"entropy": random.uniform(3.0, 5.0), "file_path": "C:\\Users\\admin\\Documents\\notes.txt"}})
    return events

def generate_malicious_event(timestamp_base, obfuscated=False):
    events = []
    if obfuscated:
        events.append({"event_type": "process_creation", "timestamp": timestamp_base, "data": {"command_line": "powershell.exe -w hidden -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACgAWwBDAG8AbgB2AGUAcgB0AF0AOgA6AEYAcgBvAG0AQgBhAHMAZQA2ADQAUwB0AHIAaQBuAGcAKAAiAEgA"}})
        events.append({"event_type": "process_creation", "timestamp": timestamp_base + 1, "data": {"command_line": "wmic.exe shadowcopy delete"}})
    else:
        events.append({"event_type": "process_creation", "timestamp": timestamp_base, "data": {"command_line": "vssadmin.exe Delete Shadows /All /Quiet"}})
        events.append({"event_type": "process_creation", "timestamp": timestamp_base + 1, "data": {"command_line": "cmd.exe /c bcdedit /set {default} recoveryenabled No"}})
    
    events.append({"event_type": "filesystem_entropy", "timestamp": timestamp_base + 2, "data": {"entropy": random.uniform(7.8, 8.0), "file_path": f"C:\\Users\\admin\\Documents\\file_{random.randint(1,100)}.enc"}})
    events.append({"event_type": "dns_query", "timestamp": timestamp_base + 4, "data": {"query": "malicious-c2-domain.xyz"}})
    return events

def main():
    dataset = {"description": "Multi-Tier Synthetic Dataset (Tiers A-D)", "samples": []}
    timestamp = 1723970000.0
    
    # Tier A: Canonical Benign (25) & Canonical Malicious (25)
    for i in range(25):
        dataset["samples"].append({"id": f"tierA-benign-{uuid.uuid4().hex[:8]}", "ground_truth": "BENIGN", "true_attck_techniques": [], "events": generate_benign_event(timestamp)})
        dataset["samples"].append({"id": f"tierA-malicious-{uuid.uuid4().hex[:8]}", "ground_truth": "MALICIOUS", "true_attck_techniques": ["T1490", "T1486"], "events": generate_malicious_event(timestamp)})
        timestamp += 10

    # Tier B & C: Ambiguous Benign (25)
    for i in range(25):
        dataset["samples"].append({"id": f"tierC-ambiguous-{uuid.uuid4().hex[:8]}", "ground_truth": "BENIGN", "true_attck_techniques": [], "events": generate_benign_event(timestamp, ambiguous=True)})
        timestamp += 10
        
    # Tier D: Obfuscated Malicious (25)
    for i in range(25):
        dataset["samples"].append({"id": f"tierD-obfuscated-{uuid.uuid4().hex[:8]}", "ground_truth": "MALICIOUS", "true_attck_techniques": ["T1490", "T1486", "T1059"], "events": generate_malicious_event(timestamp, obfuscated=True)})
        timestamp += 10
        
    with open("multi_tier_dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)
    print(f"Generated {len(dataset['samples'])} multi-tier samples.")

if __name__ == "__main__":
    main()
