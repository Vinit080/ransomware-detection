import uuid
import random
from datetime import datetime
from models.telemetry import TelemetryPayload, ProcessEvent, FileEvent, NetworkEvent

def generate_mock_ransomware_telemetry() -> TelemetryPayload:
    """Generates realistic telemetry representing a ransomware infection."""
    session_id = str(uuid.uuid4())
    
    # 1. Process Events
    processes = [
        ProcessEvent(
            pid=1024,
            process_name="explorer.exe",
            command_line="C:\\Windows\\explorer.exe",
        ),
        ProcessEvent(
            pid=4056,
            process_name="malware_payload.exe",
            command_line="C:\\Users\\Admin\\Downloads\\malware_payload.exe -silent",
            parent_pid=1024,
        ),
        ProcessEvent(
            pid=4090,
            process_name="vssadmin.exe",
            command_line="vssadmin.exe Delete Shadows /All /Quiet",
            parent_pid=4056,
        )
    ]
    
    # 2. File Events (Mass Encryption)
    files = []
    target_files = ["document.docx", "family_photo.jpg", "financials.xlsx", "database.sql"]
    for i, file in enumerate(target_files):
        # File read
        files.append(FileEvent(
            file_path=f"C:\\Users\\Admin\\Documents\\{file}",
            action="read",
            entropy=random.uniform(4.0, 5.0)
        ))
        # File encrypted and renamed
        files.append(FileEvent(
            file_path=f"C:\\Users\\Admin\\Documents\\{file}.enc",
            action="created",
            is_encrypted=True,
            entropy=random.uniform(7.8, 7.99) # High entropy typical of encrypted data
        ))
    
    # Ransom note
    files.append(FileEvent(
        file_path="C:\\Users\\Admin\\Documents\\README_DECRYPT.txt",
        action="created",
        entropy=4.2
    ))
    
    # 3. Network Events (C2 communication)
    networks = [
        NetworkEvent(
            source_ip="192.168.1.100",
            destination_ip="185.10.20.30", # Fake malicious IP
            destination_port=443,
            protocol="TCP",
            bytes_sent=2048,
            bytes_received=512,
        ),
        NetworkEvent(
            source_ip="192.168.1.100",
            destination_ip="185.10.20.30", 
            destination_port=4444, # Suspicious C2 port
            protocol="TCP",
            bytes_sent=15000,
            bytes_received=2000,
        )
    ]
    
    return TelemetryPayload(
        session_id=session_id,
        processes=processes,
        files=files,
        networks=networks
    )

def generate_benign_telemetry() -> TelemetryPayload:
    """Generates benign telemetry."""
    session_id = str(uuid.uuid4())
    processes = [
        ProcessEvent(pid=1024, process_name="explorer.exe", command_line="C:\\Windows\\explorer.exe"),
        ProcessEvent(pid=2048, process_name="chrome.exe", command_line="chrome.exe", parent_pid=1024)
    ]
    files = [
        FileEvent(file_path="C:\\Users\\Admin\\Downloads\\installer.exe", action="created", entropy=5.5)
    ]
    networks = [
        NetworkEvent(source_ip="192.168.1.100", destination_ip="142.250.190.46", destination_port=443, protocol="TCP", bytes_sent=1024, bytes_received=8048)
    ]
    return TelemetryPayload(session_id=session_id, processes=processes, files=files, networks=networks)
