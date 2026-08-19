from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from packages.schemas.models import Base
import os

# Ideally, load this from environment variables
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://ransomshield:password123@localhost/ransomshield_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
