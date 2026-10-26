from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    external_patient_id = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    date_of_birth = Column(DateTime, nullable=True)
    sex = Column(String, nullable=True)
    preferred_language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Consent(Base):
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    purpose = Column(String, nullable=True)
    scope = Column(String, nullable=True)
    consent_version = Column(String, nullable=True)
    status = Column(String, nullable=False) # "agreed" or "declined"

class ClinicalFact(Base):
    __tablename__ = "clinical_facts"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    category = Column(String, nullable=False)
    field = Column(String, nullable=False)
    value = Column(String, nullable=True)
    normalized_value = Column(String, nullable=True)
    source_type = Column(String, nullable=False)
    source_reference = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    verification_status = Column(String, default="unverified") # unverified, verified, rejected, corrected
    created_at = Column(DateTime, default=datetime.utcnow)

class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    question_id = Column(String, nullable=False)
    question_text = Column(String, nullable=False)
    answer = Column(Text, nullable=True)
    language = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    consultation_id = Column(Integer, ForeignKey("encounters.id"), nullable=True)
    uploaded_by = Column(String, nullable=True)
    hospital_id = Column(String, nullable=True)
    document_type = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    storage_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    document_date = Column(DateTime, nullable=True)
    ocr_status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Legacy compatibility aliases for existing code
    @property
    def file_path(self):
        return self.storage_path
        
    @property
    def document_name(self):
        return self.original_filename
        
    @property
    def encounter_id(self):
        return self.consultation_id

    ocr_result = relationship("OCRResult", back_populates="document", uselist=False)


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    raw_text = Column(Text, nullable=True)
    structured_output = Column(JSON, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="ocr_result")

class DoctorReview(Base):
    __tablename__ = "doctor_reviews"

    id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=False)
    reviewer_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    finalized_at = Column(DateTime, nullable=True)

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    clinical_fact_id = Column(Integer, ForeignKey("clinical_facts.id"), nullable=False)
    source_type = Column(String, nullable=False)
    source_reference = Column(String, nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    page_number = Column(Integer, nullable=True)
    excerpt = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)

    document = relationship("Document")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True) # Usually doctor_id or worker_id
    patient_id = Column(Integer, nullable=True)
    document_id = Column(Integer, nullable=True)
    consultation_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Legacy fields
    actor = Column(String, nullable=True)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
 # avoiding reserved keyword
