from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from infra.database.database import get_db
from packages.schemas.models import User
from packages.schemas.sample import SampleCreate, SampleResponse
from packages.security.rbac import RequireRole
from services.sample_manager.service import SampleManager

router = APIRouter(prefix="/api/v1/samples", tags=["samples"])

# Allowed roles for managing samples
sample_roles = RequireRole(["ANALYST", "RESEARCHER", "ADMINISTRATOR"])

@router.post("/", response_model=SampleResponse, status_code=status.HTTP_201_CREATED)
def register_sample(
    sample_in: SampleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(sample_roles)
):
    """
    Register a new research sample. 
    Requires ANALYST, RESEARCHER, or ADMINISTRATOR roles.
    """
    manager = SampleManager(db)
    return manager.create_sample(sample_in)

@router.get("/", response_model=List[SampleResponse])
def list_samples(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(sample_roles)
):
    """
    List registered research samples.
    """
    manager = SampleManager(db)
    return manager.get_all_samples(skip=skip, limit=limit)

@router.get("/{sha256}", response_model=SampleResponse)
def get_sample(
    sha256: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(sample_roles)
):
    """
    Get sample details using its canonical SHA-256 hash.
    """
    manager = SampleManager(db)
    sample = manager.get_sample_by_sha256(sha256)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample
