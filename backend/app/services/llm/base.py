from typing import Protocol, Any

class LLMProvider(Protocol):
    async def generate_structured(self, prompt: str, schema: dict) -> dict:
        ...

    def is_available(self) -> bool:
        ...
