from typing import List, Dict
from sentence_transformers import SentenceTransformer
from app.db.models import Patient, Encounter, ClinicalFact, AuditLog, DoctorReview
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .base import EmbeddingProvider, VectorStore, Retriever

class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        # CPU optimized fast embedding model
        self.model = SentenceTransformer(model_name, device="cpu")

    def get_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

class PGVectorStore(VectorStore):
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def add_documents(self, documents: List[dict]):
        # Implementation to update encounter/fact embeddings
        pass

    async def similarity_search(self, query_embedding: List[float], limit: int = 5) -> List[dict]:
        result = await self.session.execute(
            select(Encounter).order_by(Encounter.summary_embedding.l2_distance(query_embedding)).limit(limit)
        )
        encounters = result.scalars().all()
        # Mocking document metadata response as requested for the RAG architecture
        return [
            {
                "record_id": e.id, 
                "document_id": None, 
                "document_type": "encounter_summary",
                "document_name": f"Encounter_{e.id}_Summary",
                "date": e.created_at.isoformat() if e.created_at else None,
                "page_number": None,
                "text": "Encounter summary placeholder",
                "similarity": 0.95
            } 
            for e in encounters if e.summary_embedding is not None
        ]

class ClinicalRetriever(Retriever):
    def __init__(self, embedder: EmbeddingProvider, store: VectorStore):
        self.embedder = embedder
        self.store = store

    async def retrieve_relevant_history(self, current_facts: str) -> List[dict]:
        query_emb = self.embedder.get_embedding(current_facts)
        return await self.store.similarity_search(query_emb)
