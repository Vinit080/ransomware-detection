import json
import random
import uuid

def generate_benign_event(timestamp_base):
    events = [
        {"event_type": "process_creation", "timestamp": timestamp_base, "data": {"command_line": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"}},
        {"event_type": "dns_query", "timestamp": timestamp_base + 1, "data": {"query": "google.com"}},
        {"event_type": "process_creation", "timestamp": timestamp_base + 2, "data": {"command_line": "explorer.exe"}},
        {"event_type": "filesystem_entropy", "timestamp": timestamp_base + 3, "data": {"entropy": random.uniform(3.0, 5.0), "file_path": "C:\\Users\\admin\\Documents\\notes.txt"}},
    ]
    return events

def generate_malicious_event(timestamp_base):
    # Mix of techniques: T1486 (Data Encrypted), T1490 (Inhibit System Recovery), T1059 (Command and Scripting Interpreter)
    events = [
        {"event_type": "process_creation", "timestamp": timestamp_base, "data": {"command_line": "vssadmin.exe Delete Shadows /All /Quiet"}},
        {"event_type": "process_creation", "timestamp": timestamp_base + 1, "data": {"command_line": "cmd.exe /c bcdedit /set {default} recoveryenabled No"}},
        {"event_type": "filesystem_entropy", "timestamp": timestamp_base + 2, "data": {"entropy": random.uniform(7.5, 8.0), "file_path": f"C:\\Users\\admin\\Documents\\file_{random.randint(1,100)}.enc"}},
        {"event_type": "filesystem_entropy", "timestamp": timestamp_base + 3, "data": {"entropy": random.uniform(7.8, 8.0), "file_path": f"C:\\Users\\admin\\Documents\\file_{random.randint(101,200)}.enc"}},
        {"event_type": "dns_query", "timestamp": timestamp_base + 4, "data": {"query": "malicious-c2-domain.xyz"}},
    ]
    return events

def main():
    dataset = {
        "description": "Synthetic Dataset for Table III Evaluation",
        "samples": []
    }
    
    timestamp = 1723970000.0
    
    # Generate 50 Benign Samples
    for i in range(50):
        dataset["samples"].append({
            "id": f"benign-{i:03d}-{uuid.uuid4().hex[:8]}",
            "ground_truth": "BENIGN",
            "true_attck_techniques": [],
            "events": generate_benign_event(timestamp)
        })
        timestamp += 10
        
    # Generate 50 Malicious Samples
    for i in range(50):
        # We assume our malicious samples use T1490 (Inhibit System Recovery) and T1486 (Data Encrypted for Impact)
        dataset["samples"].append({
            "id": f"malware-{i:03d}-{uuid.uuid4().hex[:8]}",
            "ground_truth": "MALICIOUS",
            "true_attck_techniques": ["T1490", "T1486"],
            "events": generate_malicious_event(timestamp)
        })
        timestamp += 10
        
    with open("benchmark_dataset.json", "w") as f:
        json.dump(dataset, f, indent=4)
        
    print(f"Successfully generated synthetic dataset with {len(dataset['samples'])} samples.")

if __name__ == "__main__":
    main()
