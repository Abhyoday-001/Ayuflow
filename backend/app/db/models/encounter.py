from sqlalchemy import Column, Integer, String, DateTime
from pgvector.sqlalchemy import Vector
from datetime import datetime

from .base import Base

class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    status = Column(String, default="DRAFT") # DRAFT, IN_REVIEW, FINALIZED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Simple vector column to verify pgvector integration (e.g. for RAG embeddings of encounter summary)
    summary_embedding = Column(Vector(384))
