import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from packages.schemas.models import Sample
from packages.schemas.sample import SampleCreate

class SampleManager:
    def __init__(self, db: Session):
        self.db = db

    def get_sample_by_sha256(self, sha256: str) -> Sample:
        return self.db.query(Sample).filter(Sample.sha256 == sha256).first()

    def get_all_samples(self, skip: int = 0, limit: int = 100) -> list[Sample]:
        return self.db.query(Sample).offset(skip).limit(limit).all()

    def create_sample(self, sample_in: SampleCreate) -> Sample:
        # Enforce canonical SHA-256 uniqueness
        existing = self.get_sample_by_sha256(sample_in.sha256)
        if existing:
            raise HTTPException(status_code=409, detail="Sample with this SHA-256 already exists")

        # Create new sample
        sample = Sample(
            id=str(uuid.uuid4()),
            sha256=sample_in.sha256,
            family=sample_in.family,
            variant=sample_in.variant,
            source=sample_in.source,
            authorisation_status=sample_in.authorisation_status,
            risk_classification=sample_in.risk_classification,
            notes=sample_in.notes
        )
        self.db.add(sample)
        self.db.commit()
        self.db.refresh(sample)
        return sample
