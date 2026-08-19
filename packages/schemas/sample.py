from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SampleBase(BaseModel):
    sha256: str = Field(..., description="The canonical SHA-256 hash identifier of the sample")
    family: Optional[str] = None
    variant: Optional[str] = None
    source: Optional[str] = None
    authorisation_status: Optional[str] = Field(None, description="Legal/authorisation metadata")
    risk_classification: Optional[str] = None
    notes: Optional[str] = None

class SampleCreate(SampleBase):
    pass

class SampleUpdate(BaseModel):
    family: Optional[str] = None
    variant: Optional[str] = None
    source: Optional[str] = None
    authorisation_status: Optional[str] = None
    risk_classification: Optional[str] = None
    notes: Optional[str] = None

class SampleResponse(SampleBase):
    id: str
    acquisition_date: datetime
    model_config = {"from_attributes": True}
