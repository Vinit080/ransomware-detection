from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TelemetryEventCreate(BaseModel):
    run_id: str = Field(..., description="The ID of the SandboxRun this telemetry belongs to")
    event_type: str = Field(..., description="e.g., 'filesystem_entropy', 'api_hook', 'registry_modification'")
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    event_data: Dict[str, Any] = Field(..., description="JSON blob containing the raw telemetry metrics")
