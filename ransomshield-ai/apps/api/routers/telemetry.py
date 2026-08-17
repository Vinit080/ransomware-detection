import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from infra.database.database import get_db
from packages.schemas.models import TelemetryEvent, SandboxRun
from packages.schemas.telemetry import TelemetryEventCreate

router = APIRouter(prefix="/api/v1/telemetry", tags=["telemetry"])

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry_batch(
    events: List[TelemetryEventCreate],
    db: Session = Depends(get_db)
):
    """
    High-throughput ingestion endpoint for the in-guest telemetry agent.
    In a production setting, this endpoint would authenticate using an ephemeral token
    generated specifically for the SandboxRun to prevent spoofing.
    """
    db_events = []
    
    # Simple validation (ensure run_id actually exists and is active)
    # Note: for high throughput, we might cache active run_ids in Redis instead of querying SQL
    
    for event in events:
        db_event = TelemetryEvent(
            id=str(uuid.uuid4()),
            run_id=event.run_id,
            timestamp=datetime.now(timezone.utc),
            event_type=event.event_type,
            process_id=event.process_id,
            process_name=event.process_name,
            event_data=event.event_data
        )
        db_events.append(db_event)
        
    db.bulk_save_objects(db_events)
    db.commit()
    
    return {"detail": f"Ingested {len(db_events)} events"}
