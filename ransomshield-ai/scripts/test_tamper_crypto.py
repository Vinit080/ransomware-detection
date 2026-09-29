import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.analysis.telemetry_crypto import Sender, Receiver, TelemetryRejected, new_session_key
import random

def run_tamper_test():
    attacks_caught = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    num_repeats = 30
    
    for i in range(num_repeats):
        # Setup session
        key = new_session_key()
        sender = Sender(key)
        receiver = Receiver(key, sender.session_id)
        
        # Base sequence of events (canonical malicious trace)
        events = [
            {"event_type": "process_creation", "cmd": "vssadmin.exe delete shadows"},
            {"event_type": "process_creation", "cmd": "bcdedit /set recoveryenabled No"},
            {"event_type": "filesystem_entropy", "file": "test1.enc"},
            {"event_type": "filesystem_entropy", "file": "test2.enc"},
            {"event_type": "dns_query", "domain": "malicious.com"}
        ]
        
        # 1. Drop Event
        records = [sender.seal(e) for e in events]
        records.pop(2) # Drop middle event
        try:
            for r in records: receiver.open(r)
            receiver.finish(len(events))
        except TelemetryRejected:
            attacks_caught[1] += 1

        # Reset session
        sender = Sender(key)
        receiver = Receiver(key, sender.session_id)
        
        # 2. Reorder Events
        records = [sender.seal(e) for e in events]
        records[2], records[3] = records[3], records[2] # Swap
        try:
            for r in records: receiver.open(r)
            receiver.finish(len(events))
        except TelemetryRejected:
            attacks_caught[2] += 1
            
        # Reset session
        sender = Sender(key)
        receiver = Receiver(key, sender.session_id)
        
        # 3. Modify event data
        records = [sender.seal(e) for e in events]
        # Modify a byte in the ciphertext of the 3rd record
        modified_record = bytearray(records[2])
        modified_record[-5] ^= 0x01 # flip a bit in ciphertext
        records[2] = bytes(modified_record)
        try:
            for r in records: receiver.open(r)
            receiver.finish(len(events))
        except TelemetryRejected:
            attacks_caught[3] += 1
            
        # Reset session
        sender = Sender(key)
        receiver = Receiver(key, sender.session_id)
        
        # 4. Inject Fake Benign Event
        records = [sender.seal(e) for e in events]
        # Generate a fake record from another session or random
        fake_sender = Sender(new_session_key())
        fake_record = fake_sender.seal({"event_type": "process_creation", "cmd": "calc.exe"})
        records.insert(2, fake_record)
        try:
            for r in records: receiver.open(r)
            receiver.finish(len(events) + 1)
        except TelemetryRejected:
            attacks_caught[4] += 1

        # Reset session
        sender = Sender(key)
        receiver = Receiver(key, sender.session_id)
        
        # 5. Delay Event Delivery (Event arrives out of order, e.g. at the end)
        records = [sender.seal(e) for e in events]
        delayed = records.pop(1)
        records.append(delayed)
        try:
            for r in records: receiver.open(r)
            receiver.finish(len(events))
        except TelemetryRejected:
            attacks_caught[5] += 1

        # Reset session
        sender = Sender(key)
        receiver = Receiver(key, sender.session_id)
        
        # 6. Corrupt Event Signature (AES tag)
        records = [sender.seal(e) for e in events]
        modified_record = bytearray(records[4])
        modified_record[-1] ^= 0xFF # Corrupt GCM tag at the end
        records[4] = bytes(modified_record)
        try:
            for r in records: receiver.open(r)
            receiver.finish(len(events))
        except TelemetryRejected:
            attacks_caught[6] += 1

    print("Tamper Test (E+) Results (30 iterations each):")
    for attack, caught in attacks_caught.items():
        print(f"Attack {attack}: Caught {caught}/{num_repeats} ({caught/num_repeats*100:.0f}%)")

if __name__ == "__main__":
    try:
        import cryptography
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    
    run_tamper_test()
