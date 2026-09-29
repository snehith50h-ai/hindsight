from datetime import datetime
from typing import Sequence
from core.app.ports import MemoryPort, MemoryItem

class FakeMemory(MemoryPort):
    def __init__(self):
        self.retained = []

    async def retain(self, tenant_id: str, content: str, *, context: str, tags: Sequence[str] = (), timestamp: datetime | None = None, document_id: str | None = None) -> None:
        self.retained.append({
            "tenant_id": tenant_id,
            "content": content,
            "context": context,
            "tags": tags,
            "document_id": document_id
        })

    async def recall(self, tenant_id: str, query: str, *, tags: Sequence[str] = (), limit: int = 10) -> list[MemoryItem]:
        return [
            MemoryItem(id=f"fake-{i}", text=r["content"])
            for i, r in enumerate(self.retained)
            if r["tenant_id"] == tenant_id
        ][:limit]

    async def reflect(self, tenant_id: str, query: str, *, context: str | None = None) -> str:
        return f"Fake reflection for {query}"
