import os
import sys
import time
import json
import math
import argparse
import requests
from typing import List, Dict, Any

# A very basic entropy calculator for file contents
def calculate_entropy(file_path: str) -> float:
    try:
        with open(file_path, 'rb') as f:
            data = f.read(8192) # Read first 8KB for speed
            
        if not data:
            return 0.0
            
        entropy = 0.0
        length = len(data)
        occurrences = [0] * 256
        for byte in data:
            occurrences[byte] += 1
            
        for count in occurrences:
            if count > 0:
                p_x = count / length
                entropy -= p_x * math.log2(p_x)
                
        return entropy
    except Exception:
        return -1.0 # Error reading file

class TelemetryAgent:
    def __init__(self, ingest_url: str, run_id: str, batch_size: int = 10, batch_interval_sec: float = 2.0):
        self.ingest_url = ingest_url
        self.run_id = run_id
        self.batch_size = batch_size
        self.batch_interval_sec = batch_interval_sec
        
        self.event_queue: List[Dict[str, Any]] = []
        self.last_flush_time = time.time()
        
    def enqueue_event(self, event_type: str, event_data: Dict[str, Any]):
        event = {
            "run_id": self.run_id,
            "event_type": event_type,
            "process_id": os.getpid(),
            "process_name": "unknown", # Ideally fetched via psutil
            "event_data": event_data
        }
        self.event_queue.append(event)
        
        # Flush if we hit batch limit or time interval
        now = time.time()
        if len(self.event_queue) >= self.batch_size or (now - self.last_flush_time) >= self.batch_interval_sec:
            self.flush()
            
    def flush(self):
        if not self.event_queue:
            return
            
        batch = self.event_queue.copy()
        self.event_queue.clear()
        self.last_flush_time = time.time()
        
        try:
            # We explicitly do NOT write to disk on failure to maintain stealth.
            # If network fails, telemetry is lost (acceptable tradeoff for stealth in this design).
            resp = requests.post(self.ingest_url, json=batch, timeout=2.0)
            if resp.status_code != 202:
                print(f"Failed to ingest: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")

    # Simulated monitor function for the prototype
    def monitor_directory(self, path: str):
        print(f"Monitoring directory: {path}")
        # In a real agent, we would use 'watchdog' or ReadDirectoryChangesW (Windows API).
        # For this prototype, we simulate finding a file and calculating its entropy.
        
        # Simulate finding a file
        simulated_target = os.path.join(path, "test_file.txt")
        if os.path.exists(simulated_target):
            entropy = calculate_entropy(simulated_target)
            self.enqueue_event(
                event_type="filesystem_entropy",
                event_data={
                    "action": "FILE_MODIFIED",
                    "file_path": simulated_target,
                    "entropy": entropy
                }
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="In-Guest Telemetry Agent")
    parser.add_argument("--url", type=str, required=True, help="Ingest URL on host")
    parser.add_argument("--run-id", type=str, required=True, help="Sandbox Run ID")
    parser.add_argument("--path", type=str, default="C:\\", help="Path to monitor")
    args = parser.parse_args()
    
    agent = TelemetryAgent(ingest_url=args.url, run_id=args.run_id)
    
    try:
        while True:
            agent.monitor_directory(args.path)
            time.sleep(1)
    except KeyboardInterrupt:
        agent.flush()
        sys.exit(0)
