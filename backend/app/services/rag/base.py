from typing import Protocol, List

class EmbeddingProvider(Protocol):
    def get_embedding(self, text: str) -> List[float]:
        ...
        
class VectorStore(Protocol):
    async def add_documents(self, documents: List[dict]):
        ...
        
    async def similarity_search(self, query_embedding: List[float], limit: int = 5) -> List[dict]:
        ...

class Retriever(Protocol):
    async def retrieve_relevant_history(self, current_facts: str) -> List[dict]:
        ...
