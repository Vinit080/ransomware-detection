import copy
import random
import uuid
import json

class TamperHarness:
    def __init__(self, dataset_path="benchmark_dataset.json"):
        with open(dataset_path, "r") as f:
            self.data = json.load(f)

    def run_six_attacks(self, num_repeats=30):
        # 6 Attacks:
        # 1. Drop Event
        # 2. Reorder Events
        # 3. Modify Event Data (untrusted field)
        # 4. Inject Fake Benign Event
        # 5. Delay Event Delivery
        # 6. Corrupt Event Signature (AES/Sequence)
        
        attacked_samples = []
        
        # We take canonical malicious samples to attack
        malicious_samples = [s for s in self.data.get("samples", []) if s["ground_truth"] == "MALICIOUS"]
        
        if not malicious_samples:
            return attacked_samples
            
        for i in range(num_repeats):
            for attack_type in range(1, 7):
                base_sample = copy.deepcopy(random.choice(malicious_samples))
                base_sample["id"] = f"tampered-A{attack_type}-R{i}-{uuid.uuid4().hex[:8]}"
                base_sample["telemetry_tampered_ground_truth"] = True
                
                events = base_sample["events"]
                if not events: continue
                
                if attack_type == 1:
                    # Drop a random event
                    events.pop(random.randint(0, len(events)-1))
                elif attack_type == 2:
                    # Reorder two events
                    if len(events) >= 2:
                        idx1, idx2 = random.sample(range(len(events)), 2)
                        events[idx1], events[idx2] = events[idx2], events[idx1]
                elif attack_type == 3:
                    # Modify untrusted field
                    ev = events[random.randint(0, len(events)-1)]
                    if "data" in ev and isinstance(ev["data"], dict):
                        for k in ev["data"].keys():
                            ev["data"][k] = "TAMPERED_DATA"
                elif attack_type == 4:
                    # Inject Fake Benign
                    events.insert(random.randint(0, len(events)), {
                        "event_type": "process_creation",
                        "timestamp": events[0]["timestamp"],
                        "data": {"command_line": "calc.exe"}
                    })
                elif attack_type == 5:
                    # Delay event delivery
                    ev = events[random.randint(0, len(events)-1)]
                    ev["timestamp"] += 10000 
                elif attack_type == 6:
                    # Corrupt signature / sequence
                    ev = events[random.randint(0, len(events)-1)]
                    ev["signature"] = "CORRUPTED_AES_GCM_MAC"
                    ev["sequence_number"] = -1
                
                base_sample["events"] = events
                attacked_samples.append(base_sample)
                
        return attacked_samples

if __name__ == "__main__":
    harness = TamperHarness()
    results = harness.run_six_attacks(num_repeats=30)
    print(f"Generated {len(results)} tampered traces.")
    
    with open("tampered_dataset.json", "w") as f:
        json.dump({"description": "Tamper Test (E+) 6 attacks x 30 repeats", "samples": results}, f, indent=4)
