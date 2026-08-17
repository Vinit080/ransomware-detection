from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ProcessEvent(BaseModel):
    pid: int
    process_name: str
    command_line: str
    parent_pid: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FileEvent(BaseModel):
    file_path: str
    action: str  # e.g., 'created', 'modified', 'deleted', 'renamed'
    is_encrypted: bool = False
    entropy: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NetworkEvent(BaseModel):
    source_ip: str
    destination_ip: str
    destination_port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TelemetryPayload(BaseModel):
    session_id: str
    processes: List[ProcessEvent] = []
    files: List[FileEvent] = []
    networks: List[NetworkEvent] = []
